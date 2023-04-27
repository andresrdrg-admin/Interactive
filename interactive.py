import pexpect
import threading


class Interactive:
    def __init__(self, cmd):
        self.cmd = cmd
        self.code = "En espera"
        
    def interact(self,  await_messages):
        self.await_messages = await_messages
        self.child = pexpect.spawn(self.cmd)
        threading.Thread(target=self.subprocess).start()

        
    def subprocess(self):
        iter_count = 0
        for await_message in self.await_messages:
            iter_count += 1
            while True:
                if(self.child.before != ""):
                    output = self.child.expect([pexpect.EOF, pexpect.TIMEOUT, await_message['question']], timeout=25)
                    if output == 0:
                        self.code = (f"""Fallo""")
                    elif output == 1:
                        self.code = (f"""Tiempo de espera agotado para {await_message['question']} \n\n """)
                    else:
                        self.child.sendline(await_message['response'])
                        self.code = (f"""Conectado -  """)
                        if(iter_count < len(self.await_messages)):
                            break