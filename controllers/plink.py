from multiprocessing import Process, Manager
from libs.interactive.interactive import Interactive
import time


class InteractivePLink():
    
    def __init__(self, credentials, sleep_executions) -> None:
        self.creadentials = credentials
        self.sleep_executions = sleep_executions
        self.connections = Manager().dict()
    
    def create_connection(self, name_connection, port_local, port_bridge, port_objetive, trace_ips, bridge ="localhost"):
        cmd = f"plink -L {port_local}:{bridge}:{port_bridge} "
        await_messages = [
            {
                "question": "Access granted. Press Return to begin session.",
                "response" : ""
            }
        ]
        i = 0
        for ip in trace_ips:
            i += 1
            if i == 1:
                cmd += f"{self.creadentials[ip]['user']}@{ip} -pw {self.creadentials[ip]['password']} -t "
            else:
                await_messages.append(
                    {
                        "question": f"{self.creadentials[ip]['user']}@{ip}'s password:",
                        "response" : self.creadentials[ip]['password']
                    }
                )
                cmd += f"ssh -L {port_bridge}:"
                cmd += f"localhost" if i < len(trace_ips) else bridge
                cmd += f":{port_bridge if i < len(trace_ips) else port_objetive} {self.creadentials[ip]['user']}@{ip}"
                cmd += " -t " if i < len(trace_ips) else ""
        await_messages.append(
            {
                "question": f"lnxipdr2:/home/{self.creadentials[ip]['user']}>",
                "response": ""
            }
        )
        proccess_connect = Process(target=self.connect, args=(cmd, await_messages, name_connection))
        proccess_connect.start()
        
    def connect(self, cmd, await_messages, name_conection):
        while True:
            interactive_call = Interactive(cmd=cmd, await_messages=await_messages, name_conection=name_conection)
            while True:
                if ("Fallo" in interactive_call.code.value):
                    self.connections[name_conection] ="Reconectando..."
                    break
                
                self.connections[name_conection] = f"""{
                    interactive_call.code.value
                    } {
                    f"{interactive_call.console.value}" if("Tiempo de espera agotado" in interactive_call.code.value) else ""
                    }"""
            
                time.sleep(self.sleep_executions)
        