#!/usr/bin/env python3
# encoding: utf-8


from cmd import Cmd
import pickle
import subprocess
import os
import random
from collections import OrderedDict

ssh = True
hostList = ['localhost']  # change for your needs 
session_file = os.path.expanduser('~/.sessions')


class SessionsShell(Cmd):
    """Simple command line interface for managing tmux _sessions"""
    def __init__(self, hosts = ['localhost']):
        super().__init__()
        self.intro = "Welcome"
        self.prompt = "(session manager)> "
        self.hosts = hosts

        try:
            with open(session_file, 'br') as saved_file:
                self._sessions = pickle.load(saved_file)
        except FileNotFoundError:
            self._sessions = OrderedDict()


    #########################
    #  Command Definitions  #
    #########################


    def do_sshtest(self, args):
        cmd = ['ssh', '-t', 'localhost',
                ['/bin/sh', '-lc', args]]

        print(cmd)
        ret = subprocess.call(cmd)
        print("RETVAL=={}".format(ret))

    def do_shell(self, args):
        subprocess.call(args, shell=True)


    def do_ls(self, args):
        """ls 
        
        Print all existing sessions.
        :type args: str

        """
        arglist = args.split()
        if not self._sessions:
            print("No sessions found")
        for i, s in enumerate(self._sessions):
            if '-a' in arglist:
                width = max([len(session_name) for session_name in self._sessions])
                print("{}: {:{w}}  |  {}".format(i, s, self._sessions[s], w=width))
            else:
                print(i,': ',  s)

        print()

    def do_la(self, args):
        """la

        Same as 'ls -a'
        """
        self.do_ls('-a')

    def do_new(self, name):
        """new NAME
        
        Create a new session and connect to it

        :type name: str
        """
        if not name:
            print("Invalid usage. see 'help new'")
        if name in self._sessions:
            print("Session already exists")
            return
        cmd = 'tmux.py new "{}"'.format(name)

        host, ret = self._exec_cmd(cmd)
        if ret is 100: # tmux detached 
            self._sessions[name] = host
            self._sessions.move_to_end(name, last=False)
        

    def do_attach(self, name):
        """Attach to an existing session

        :name: TODO
        :type name: str
        :returns: TODO

        """
        if not name:
            print("Invalid usage. see 'help new'")
        if name not in self._sessions:
            print("Session does not exist")
            return
        cmd = 'tmux.py attach "{}"'.format(name)

        host, ret = self._exec_cmd(cmd, self._sessions[name])
        if ret is 200:  # tmux exited 
            del self._sessions[name]
        else:
            self._sessions.move_to_end(name, last=False)


    def do_kill(self, name):
        """TODO: Docstring for do_kill.

        :type name: str

        """

        if name == '*':
            for s in self._sessions[:]:
                self.do_kill(s)

            return
        
        if name not in self._sessions:
            print("Session does not exist")
            return
        cmd = 'tmux.py kill "{}"'.format(name)

        host, ret = self._exec_cmd(cmd, self._sessions[name])
        if ret is 0 or ret is 1:  # tmux returned normally or session wasn't found
            del self._sessions[name]


    def do_rename(self, name):
        """rename OLD_NAME
        
        Rename a session.  Will prompt for new name. 

        :args: TODO
        :type args: str
        :returns: TODO

        """

        if not name:
            print("Invalid usage. see 'help new'")
        if name not in self._sessions:
            print("Session does not exist")
            return

        new_name = input('New name: ')

        cmd = 'tmux.py rename "{}" --new_name "{}"'.format(name, new_name)

        host, ret = self._exec_cmd(cmd, self._sessions[name])

        if ret is 0:  # returned normally
            self._sessions[new_name] = self._sessions.pop(name)
            self._sessions.move_to_end(new_name, last=False)

    
        

    ############################
    #  Completion definitions  #
    ############################
    

    def completedefault(self, text, line, begidx, endidx):
        """TODO: Docstring for test.

        :arg1: TODO
        :returns: TODO

        """
        arg = line.partition(' ')[2]  # get the part of the line after the first space
        offset = len(arg) - len(text)
        return [s[offset:] for s in self._sessions if s.startswith(arg)]



    ############################
    #  Commands to exit shell  #
    ############################

    def do_EOF(self, args):
        print('\n')
        self._quit()
        return True

    def do_exit(self, args):
        self._quit()
        return True

    def do_quit(self, args):
        self._quit()
        return True

    def do_bye(self, args):
        self._quit()
        return True

    def postcmd(self, stop, line):
        with open(session_file, 'wb') as saved_file:
            pickle.dump(self._sessions, saved_file)

        if stop is True:
            return True


    ####################
    #  Helper methods  #
    ####################


    #def _check_index(self, index_str):
        #"""
        #Checks if index given as string is valid.  
        #Returns -1 if invalid, 'index' as int otherwise
        #"""
        #if not index_str.isdigit():
            #return -1

        #index = int(index_str)

        #if index >= len(self._sessions):
            #return -1

        #return index
    
    def _exec_cmd(self, cmd, host=None):
        '''
        returns a tuple containing:
            the hostname it connected to,
            and:
                100 if tmux.py session detached,
                200 if tmux.py session exited
                0 if tmux.py exited otherwise successfully
                otherwise whatever return code to signify an error tmux wants

        '''
        illegals_found = [char for char in [';', '|', '*'] if char in cmd]
        if illegals_found:
            print('Illegal character found: [{}]'.format(', '.join(illegals_found)))
            return None, 1

        # build up command
        if not host:
            host = random.choice(self.hosts)
        ssh_cmd = ['ssh', '-Xt', host]

        # build remote command, escaping it appropriately. 
        rem_cmd = '/bin/sh -lc "{}"'.format(cmd.replace('"', r'\"'))

        ssh_cmd.append(rem_cmd)

        # execute command
        ret = subprocess.call(ssh_cmd)
        return host, ret # tmux.py returns 0 if 'detached' is found, and >0 otherwise

    def _quit(self):
        print("Goodbye!\n")
    


def main():
    """Main function.  Runs an instance of SessionsShell
    :returns: TODO

    """
    shell = SessionsShell(hostList)
    shell.cmdloop()


if __name__ == '__main__':
    main()
