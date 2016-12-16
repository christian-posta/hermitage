#!/usr/bin/python
import sys
import os
import signal
import time
import re


def parseFile(raw_file):
    blocks = []
    with open(raw_file, "r") as file:
        
        # let's clean out all empty lines'
        clean_file = []
        for line in file:
            if line.rstrip():
                clean_file.append(line)

        
        for idx, line in enumerate(clean_file):
            if line.startswith("```sql"):
                title = clean_file[idx -1]

                # grab all lines for this block
                block_lines = []
                found_end = False
                current_idx = idx
                while True:
                    if clean_file[current_idx+1].startswith("```"):
                        break;
                    else:
                        sql_line = clean_file[current_idx + 1]
                        regex = re.compile("(T[1-3]?)")
                        match  = regex.search(sql_line)
                
                        session_number = 1 if not match else match.group(0).lstrip("T")
                        block_lines.append((session_number, sql_line))
                        current_idx += 1
                blocks.append((title,block_lines))
    return blocks

def print_blocks(blocks):
    for block in blocks:
        
        print "Title: " + block[0]
        for sql_line in block[1]:
            print "Session " + str(sql_line[0]) + " is: " + sql_line[1]
        print "\n\n"    

def next_step(session, message):
    raw_input("Next (T" + str(session) + "): " + message.replace("\n", ""))    

def setup_windows():
    for i in range(3):
        os.system('tmux split-window -v')
        os.system('tmux send-keys -t '+ str(i + 1) +' "clear" C-m')
    
    os.system('tmux select-layout even-vertical')
    os.system('tmux select-pane -t 0')

def run_in_session(session, sql):
    os.system('tmux send-keys -t '+ str(session) + ' "'+sql+'"')        

def start_db_sessions(db_client):

    for i in range(3):
        os.system('tmux send-keys -t'+str(i+1)+'  "' + db_client + '" C-m')
    

    raw_input("Set up database")
    
    print "setting up session: "
    run_in_session(1, "drop database if exists hermitage;\n")
    run_in_session(1, "create database hermitage;\n")
    run_in_session(1, "use hermitage;\n")
    run_in_session(2, "use hermitage;\n")
    


def reset_test(setup_block):
    run_in_session(1, 'drop table if exists test;\n')
    for block in setup_block:
        run_in_session(block[0], block[1])
    run_in_session(1, 'select * from test;\n')
        
        
    

   

def main():

    raw_file = sys.argv[1]
    db_client = sys.argv[2]
    print "Using testfile: " + raw_file  + " and database client: " + db_client 
    
    # format is (title, (session_number, sql_line))
    blocks = parseFile(raw_file)
    
    #print_blocks(blocks)

    setup_windows() 

    start_db_sessions(db_client)

    setup_block = blocks[0][1]
    # skip first block as thats the setup case
    for block in blocks[1:]:
        print ">>> New Test: " + block[0] 
        raw_input()
        reset_test(setup_block)
        
        for sql_line in block[1]:
            next_step(sql_line[0], sql_line[1])
            run_in_session(sql_line[0], sql_line[1])
        print "<<< End Test: " + block[0]
         
        raw_input()
    cleanup_tmux()
             
def cleanup_tmux():
    print "cleaning up"
    os.system('tmux send-keys -t 2 "exit" C-m')
    os.system('tmux send-keys -t 1 "exit" C-m')
    time.sleep(1)

    # order of killing panes matters here
    for i in reversed(range(3)):
        os.system('tmux kill-pane -t ' + str(i+1))
        time.sleep(1)
        
def signal_handler(signal, frame):
    cleanup_tmux()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Call with testfile.md and database client as parameters:
# parser.py mysql.md mysql        
if __name__ == "__main__":
    if not len(sys.argv) == 3:
        print "Call this script with the test file and db client as params: "
        print "python parser.py mysql/mysql.md mysql/mysql.sh"
        sys.exit(1)
    main()        