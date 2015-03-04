#!/usr/bin/env python3
# encoding: utf-8

import subprocess
import argparse
import sys


class Tmux:
    """Wrapper class around tmux that returns more helpful codes.
    
    Returns:
        0 if tmux detached.
        2 if tmux exited
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

        
    def _exec_tmux_cmd(self, cmd):
        """executes tmux cmd and returns a code dependent on the result

        :type cmd: str
        """
        try:
            tmux_output = subprocess.check_output(cmd)
            print(tmux_output.decode())
            if tmux_output.find(b'detached') >= 0:
                return 100
            elif tmux_output.find(b'exited') >= 0:
                return 200
            else: 
                return 0
        except subprocess.CalledProcessError as e:
            print(e.output.decode(), end='')
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
