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
        if output.find('failed'):
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
    parser = argparse.ArgumentParser(description="A wrapper around Tmux providing some basic functionality"
            "and more useful return codes")
    parser.add_argument('action', choices=('new', 'attach', 'rename', 'kill'),
            help='The action to make tmux perform')
    parser.add_argument('name', help='The name of the target session')
    parser.add_argument('--new_name', help='specify new name for session.  Ignored unless ACTION is "rename"')

    args = parser.parse_args()

    # execute tmux stuff
    tmux = Tmux()
    if args.action == 'rename':
        retval = tmux.rename(args.name, args.new_name)
    else:
        method = getattr(tmux, args.action)
        retval = method(args.name)
        
    #print('tmux.py retuned: {}'.format(retval))
    sys.exit(retval)


if __name__ == '__main__':
    main()
