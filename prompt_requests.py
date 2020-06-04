import cmd
import requests
import json

class prompt(cmd.Cmd):
    """Command line input prompt"""
    prompt = " (Type <help> to see available commands)\n: "

    def emptyline(self):
        return False

    def precmd(self, line):
        return cmd.Cmd.precmd(self, line)

    def postcmd(self, stop, line):
        return cmd.Cmd.postcmd(self, stop, line)

    def do_quit(self, arg):
        """Close the program"""
        quit()

    def do_request(self, arg):
        """Send a GET api request to the URL specified"""
        global response
        response = requests.get(arg).json()
        print(json.dumps(response, indent=4))
        response = False # Clear the variable after printing to rule out repeated attempts printing old results

    # def do_print(self, arg):
    #     """Display the response of the last api request"""
    #     print(json.dumps(response, indent=4))

if __name__ == '__main__':
    running = True
    while running == True:
        prompt().cmdloop()