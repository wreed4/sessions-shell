#!/usr/bin/env python3
# encoding: utf-8

import subprocess
import argparse
import sys

TMUX_DETACHED = 100
TMUX_EXITED   = 200

class Tmux:
    """Wrapper class around tmux that returns more helpful codes.
    
    Returns:
        TMUX_DETACHED if tmux detached.
        TMUX_EXITED if tmux exited
        tmux return code otherwise
    """

    def __init__(self):
        pass

    def new(self, session_name):
        """make a new session on the specified host

        :session_name: TODO
        :returns: TODO

        """
        cmd = ['tmux',
               'new-session',
               '-s',
               session_name]

        return self._exec_tmux_cmd(cmd)

        
    def attach(self, session_name=None):
        """attach to an existing session

        :session_name: TODO
        :returns: TODO

        """
        cmd = ['tmux', 'attach']
        if session_name:
            cmd.extend(['-t', session_name])

        return self._exec_tmux_cmd(cmd)

    
    def rename(self, old, new):
        """rename a session

        :old: TODO
        :new: TODO
        :returns: TODO

        """
        cmd = ['tmux',
               'rename-session',
               '-t',
               old,
               new]

        return self._exec_tmux_cmd(cmd)


    def kill(self, session_name):
        """kill an existing session

        :session_name: TODO
        :returns: TODO

        """
        cmd = ['tmux',
               'kill-session',
               '-t',
               session_name]

        return self._exec_tmux_cmd(cmd)


    def ls(self):
        '''
        List all running tmux sessions
        '''
        cmd = ['tmux', 'ls']

        ret, output = self._exec_tmux_cmd(cmd, output=True)
        # check for 'failed' in output
        if output.find('failed') >= 0:
            print("No sessions found")
        else:
            print(output)


        
    def _exec_tmux_cmd(self, cmd, output=False):
        """executes tmux cmd and returns a code dependent on the result

        :type cmd: str
        :return: (retcode, output) IF output ELSE retcode
        """
        try:
            tmux_output = subprocess.check_output(cmd)
            if tmux_output.find(b'detached') >= 0:
                return TMUX_DETACHED
            elif tmux_output.find(b'exited') >= 0:
                return TMUX_EXITED
            else: 
                if output:
                    return (0, tmux_output.decode())
                else:
                    print(output)
                    return 0
        except subprocess.CalledProcessError as e:
            if output:
                return (e.returncode, tmux_output.decode())
            else:
                print(output)
                return e.returncode



def main():
    # parse args
    parser = argparse.ArgumentParser(description="A wrapper around Tmux providing some basic functionality "
            "and more useful return codes")
    subcommands = parser.add_subparsers(dest='action')

    # parse 'ls'
    ls_cmd = subcommands.add_parser('ls', help='Print all tmux sessions available')

    # parse 'new', 'attach', 'kill'
    new_cmd    = subcommands.add_parser('new', help='Create a new tmux session')
    attach_cmd = subcommands.add_parser('attach', help='Attach to a currently existing tmux session')
    kill_cmd   = subcommands.add_parser('kill', help='Kill a currently running tmux session')
    for cmd in (new_cmd, attach_cmd, kill_cmd):
        cmd.add_argument('target', help='The name of the target session')

    # parse 'rename'
    rename_cmd = subcommands.add_parser('rename', help='Rename an existing tmux session')
    rename_cmd.add_argument('target', help='The name of the target session')
    rename_cmd.add_argument('new_name', help='The new name for the session')



    args = parser.parse_args()

    # execute tmux stuff
    tmux = Tmux()
    if args.action == 'rename':
        retval = tmux.rename(args.target, args.new_name)
    elif args.action == 'ls':
        retval = tmux.ls()
    else:
        method = getattr(tmux, args.action)
        retval = method(args.target)
        
    #print('tmux.py retuned: {}'.format(retval))
    sys.exit(retval)


if __name__ == '__main__':
    main()
