import platform
import time
import sys
import os
from multiprocessing import Process, Manager
from pexpect.popen_spawn import PopenSpawn
import pexpect
    
    
class Interactive:
    def __init__(self, cmd, await_messages=None, name_conection="Interactive"):
        self.cmd = cmd
        self.await_messages = await_messages
        self.name_connection = name_conection
        self.code = Manager().Value('c', 'En espera')
        self.console = Manager().Value('c', '')
        console_process = Process(name=name_conection,target=self.interactive_with_console)
        console_process.start()
    
    def write_to_file(self, dir, message):
        try:
            if os.path.isfile(dir):
                message = (str(message).split('$')[-1])[-200:]
                with open(dir, "r") as file:
                    lines = file.readlines()
                
                if len(lines) > 20:
                    self.clean_to_file(dir, "...")
            else:
                lines = None

            # Verificar si la última línea del archivo es igual a la nueva línea
            if not lines or message != lines[-1].strip():
                with open(dir, "a") as file:
                    file.write(f"{message}\n")
        except IOError:
            print(f"No se pudo editar y guardar el archivo '{dir}'.")
            
    def clean_to_file(self, dir, message):
        try:
            with open(dir, "w") as file:
                file.write(f"{message}\n")
        except IOError:
            print(f"No se pudo editar y guardar el archivo '{dir}'.")
        
    def interactive_with_console(self):
        current_dir = os.path.dirname(sys.executable)

        # Validar si existe la carpeta de logs
        current_dir_logs = f"{current_dir}/logs/{self.name_connection}"
        if(os.path.exists(current_dir_logs) == False and os.path.isdir(current_dir_logs) == False):
            os.makedirs(current_dir_logs)
        # Validar si existe el archivo para la conexión
        file_log = f"{current_dir_logs}/{self.name_connection}.log"
        if(os.path.exists(file_log) == False):
            self.write_to_file(file_log, self.cmd)
        else:
            self.clean_to_file(file_log, self.cmd)
        try:
            if platform.system() != "Windows":
                self.child = pexpect.spawn('/bin/bash', ['-c', self.cmd], timeout=None)
            else:
                self.child = pexpect.popen_spawn.PopenSpawn(f'cmd /c {self.cmd}', timeout=None)
            
            if self.await_messages != None:
                iter_count = 0
                for await_message in self.await_messages:
                    iter_count += 1
                    while True:
                        self.write_to_file(file_log, f"\"{self.child.before}\"")
                        
                        if(self.child.before != None and "Store key in cache? (y/n, Return cancels connection, i for more info)" in str(self.child.before)):
                            self.child.sendline("y")
                            self.code.value = f"""Se aceptaron condiciones de la llave para SSL"""
                            break
                        
                        output = self.child.expect([pexpect.EOF, pexpect.TIMEOUT, await_message['question']], timeout=1)
                        if await_message['response'] != "":
                            self.write_to_file(file_log, f" > \"{await_message['response']}\"")
                        
                        if output == 0:
                            self.code.value = f"Error : \"{self.child.before}\""
                            self.write_to_file(file_log, f"Error : \"{self.child.before}\"")
                        elif output == 1 and platform.system() != "Windows":
                            self.code.value = f"Tiempo de espera agotado : \"{self.child.before}\""
                            self.write_to_file(file_log, f"Tiempo de espera agotado : \"{self.child.before}\"")
                        else:
                            self.child.sendline(await_message['response'])
                            
                            self.code.value = f" > \"{self.child.before}\""
                            if(iter_count < len(self.await_messages)):
                                self.write_to_file(file_log, f" > \"{self.child.before}\"")
                                break
                            
                        time.sleep(5)
            else:
                self.child.expect(pexpect.EOF)
        except pexpect.EOF as e:
            print(f"Error al ejecutar el comando: {e}")
        