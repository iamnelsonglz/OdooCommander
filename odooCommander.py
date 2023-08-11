import atexit
import datetime
import os
import readline
import subprocess

class OddoCommander :

    def __init__ (self):

        # Inicializar las variables self.database_name y self.module
        self.database_name = ''
        self.module = ''


        #Revisar si existe el archivo data.txt y si no existe crearlo
        if not os.path.exists('data.txt'):
            with open('data.txt', 'w') as f:
                f.write("db,default \n")
                f.write("module,all")
        
        # Leer el archivo data.txt y guardar el dato de la clave db en la variable self.database_name y el dato de la clave module en la variable self.module
        with open('data.txt', 'r') as f:
            for line in f:
                if line.startswith('db'):
                    self.database_name = line.split(',')[1].strip()
                if line.startswith('module'):
                    self.module = line.split(',')[1].strip()

        # Llamar al metodo menu 
        self.menu_options = {
            "0": self.close_program,
            "1": self.update_all_modules,
            "2": self.update_module,
            "3": self.update_translations,
            "4": self.restart_odoo,
            "5": self.show_logs,
            "6": self.change_expiration_date,
            "7": self.set_parameters,
            "8": self.terminal_mode,
            "9": self.run_unit_tests,
            "10": self.clear_screen
        }


        self.menu()
    
    def show_title(self):
        print("""
  __         _                
 /  )_/     / )  _  _  _   _/_ _ 
(__/(/()() (__()//)//)(//)(/(-/                                                                                     
=============================================
""")
        print(f"  💻  Base actual {self.database_name} | Modulo actual {self.module} 💻")

    def menu (self):
        # Inicializar la variable selected_option
        selected_option = ''
        # Ciclo para mostrar el menu
        while selected_option !=0 :
            
            self.show_title()
            
            print("""\
    0. Salir
    1. Actualizar la base
    2. Actualizar módulo(s)
    3. Actualizar traducciones
    4. Reiniciar Odoo
    5. Mostrar Logs
    6. Cambiar fecha de caducidad a base de datos
    7. Definir parametros [Base de datos y Modulo(s)]
    8. Odoo en modo terminal
    9. Ejecutar Pruebas Unitarias
    10. Limpiar Pantalla
            """)

            selected_option = input("Acción a realizar: ")
            if selected_option in self.menu_options:
                self.menu_options[selected_option]()
            else:
                print("Opción no válida. Intente nuevamente.")

    def close_program(self):
        print("Adios")
        exit()

    def update_all_modules(self):
        if self.yes_no_option(f"Se detendra el servicio de Odoo y se actualizara toda la base {self.database_name} desea continuar ? "):
            command = "sudo systemctl restart odoo"
            print("Deteniendo Odoo...")
            os.system(command)
            print(" ✔️  Servicio detenido. Actualizando Modulos...")
            # Llamar al metodo update_odoo_modules y pasarle como parametro el nombre de la base y el modulo                    
            self.update_odoo_modules(self.database_name,'all')
            time = datetime.datetime.now()
            print("=============================================")                    
            print(f"El proceso de actualizacion de todos los modulos ha finalizado (⏳ {time.hour}:{time.minute}:{time.second})")
            print("El servicio de Odoo se ha iniciado")
            print("=============================================")

    def update_module(self):
        if self.yes_no_option(f"Se actualizara la base {self.database_name} con {self.module} desea continuar ? "):
            # Llamar al metodo update_odoo_modules y pasarle como parametro el nombre de la base y el modulo
            self.update_odoo_modules(self.database_name,self.module)
            time = datetime.datetime.now()
            print("=============================================")
            print(f"El proceso de actualizacion del modulo ha finalizado (⏳ {time.hour}:{time.minute}:{time.second})")
            print("=============================================")
            
    def update_translations(self):
        if self.yes_no_option(f"Se actualizaran las traducciones {self.database_name} desea continuar ? "):
            # Llamar al metodo update_odoo_modules y pasarle como parametro el nombre de la base y el modulo                    
            self.update_traduction(self.database_name)
            print("=============================================")
            print("➡ Reiniciar sistema para que los cambios surtan efecto")
            print("=============================================")

    def restart_odoo(self):
        if self.yes_no_option("Se reiniciara Odoo desea continuar ? "):
            # Reinicia odoo con el comando systemctl
            restart_command = "sudo systemctl restart odoo"
            print("Reiniciando Odoo...")
            os.system(restart_command)
            time = datetime.datetime.now()
            print("=============================================")
            print(f"➡ Reinicio completado (⏳ {time.hour}:{time.minute}:{time.second})")
            print("=============================================")

    def show_logs(self):
        # Inicializar la variable menu_logs_selected_option
        menu_logs_selected_option = ''
        # Ciclo para mostrar el menu
        while menu_logs_selected_option !=0 :
            self.show_title()
                    
            print("""\
    1. Mostrar log filtrado root (Nueva ventana)
    2. Mostrar log sin filtrado (Nueva ventana)
    0. Regresar...
                    """)
            menu_logs_selected_option = input("Acción a realizar: \n")

            if menu_logs_selected_option == "0":
                self.menu()

            if menu_logs_selected_option == "1":
                if self.yes_no_option("Se mostrara el log filtrado por root desea continuar ?"):
                    # Ejecuta el comando tail para mostrar el log filtrado por root en una nueva ventana por medio de grep
                    self.execute_command_new_terminal("echo 'Mostrando log de root:' && sudo tail -f /var/log/odoo/odoo-server.log | grep root")
            
            if menu_logs_selected_option == "2":
                if self.yes_no_option("Se mostrara el log sin filtrar desea continuar ?"):
                    # Ejecuta el comando tail para mostrar el log sin filtrar por grep en una nueva ventana
                    self.execute_command_new_terminal("echo 'Mostrando log sin filtrar:' && sudo tail -f /var/log/odoo/odoo-server.log")

    def change_expiration_date(self):
        if self.yes_no_option("Desea cambiar la fecha de caducidad de la base de datos ?"):
            # Obtener la fecha actual y sumarle 1 mes para actualizar la fecha de caducidad
            expiration_date = datetime.date.today() + datetime.timedelta(days=30)
            # Ejecutar el comando psql para actualizar la fecha de caducidad
            os.system(f"sudo -u odoo psql -d {self.database_name} -c \"UPDATE ir_config_parameter SET value = '{expiration_date}' WHERE key='database.expiration_date';\"")
            print(f"La fecha de caducidad de la base de datos {self.database_name} se actualizo a {expiration_date}")
            print("➡ Reiniciar sistema para que los cambios surtan efecto")           

    def set_parameters(self):
                
        # Inicializar la variable menu_parameters_selected_option
        menu_parameters_selected_option = ''
        # Ciclo para mostrar el menu
        while menu_parameters_selected_option !=3:
            self.show_title()
        
            print("""\
    1. Cambiar de base
    2. Cambiar modulo(s)
    0. Regresar...
                    """)

            menu_parameters_selected_option = input("Acción a realizar: \n")

            if menu_parameters_selected_option == "0":
                self.menu()

            if menu_parameters_selected_option == "1":                    
                print("Puedes usar tab para autocompletar el nombre de la base de datos")
                # Ejecutar el comando psql para obtener el listado de bases de datos
                #command_psql = "psql -h localhost -U odoo -d postgres -1 -c '\l'" 
                command_psql = "psql -U odoo -l -t | cut -d'|' -f 1 | sed -e 's/ //g' -e '/^$/d'"
                process = subprocess.Popen(command_psql, stdout=subprocess.PIPE, shell=True)
                # Obtener la salida del comando
                output, error = process.communicate()
                # Guardar cada linea en una lista y luego imprimirlo
                self.data_bases_list = [""]
                for line in output.decode("utf-8").splitlines():
                    self.data_bases_list.append(f"{line}")
                    print(line)

                # Configurar la autocompletación con la lista de elementos
                def completer(text, state):
                    options = [x for x in self.data_bases_list if x.startswith(text)]
                    if state < len(options):
                        return options[state]
                    else:
                        return None

                readline.set_completer(completer)
                readline.parse_and_bind("tab: complete")

                # Inicializar la variable bandera
                bandera = False
                while bandera == False:
                    self.database_name = input("Ingresa el nombre de la base de datos: ")
                    # verificar si la base de datos ingresada existe en line y si no existe mostrar un mensaje de error
                    if self.database_name not in self.data_bases:
                        print("LA BASE DE DATOS INGRESADA NO EXISTE!!!")
                    else:   
                        bandera = True
            if menu_parameters_selected_option == "2":
                if self.yes_no_option(f"Modulo actual {self.module} desea cambiarlo? "):
                    self.module = input("Ingresa el nombre del modulo (si son varios separar signo de coma sin usar espacios ejemplo modulo1,modulo2) ")

            # Guardar los datos de las variables self.database_name y self.module en el archivo data.txt
            with open('data.txt', 'w') as f:
                f.write(f"db,{self.database_name}\n")
                f.write(f"module,{self.module}")

    def terminal_mode(self):
        if self.yes_no_option("Se ejecutara Odoo en modo terminal desea continuar ? "):
            self.execute_command_new_terminal(f"echo 'Iniciando odoo en modo terminal:' && sudo -u odoo odoo shell -c /etc/odoo/odoo.conf -d {self.database_name}")
                    
    def run_unit_tests(self):
        if self.yes_no_option("Se ejecutaran pruebas unitarias del modulo seleccionado desea continuar ? "):
            self.execute_command_new_terminal(f"echo 'Iniciando pruebas unitarias:' && sudo odoo --test-enable --stop-after-init -d '{self.database_name}' -i '{self.module}' -c /etc/odoo/odoo.conf")

    def clear_screen(self):
        os.system("clear")

    def update_odoo_modules (self,db_name,module):
        #Funcion que recibe dos parametros el nombre de la base de datos y el modulo a actualizar para completar el comando y ejecutarlo
        command = f"sudo -u odoo odoo -c /etc/odoo/odoo.conf -d {db_name} -u {module} -p 8069 --no-http --load-language=es_MX --stop-after-init"
        os.system(command)

    def update_traduction (self,db_name):
        #Funcion que recibe un parametro el nombre de la base de datos para completar el comando y ejecutarlo
        command = f"sudo -u odoo odoo -c /etc/odoo/odoo.conf -d {db_name} -p 8069 --no-http --load-language=es_MX --stop-after-init" 
        os.system(command)

    def yes_no_option (self,message):
        #Funcion que recibe un parametro el mensaje a mostrar y devuelve True si la respuesta es S o s y False si la respuesta es N o n
        option = input (f"{message} (S/N) \n")
        if option == "S" or option == "s":
            return True
        else:
            return False

    def execute_command_new_terminal (self,command):
        # Funcion que recibe un parametro el comando a ejecutar y lo ejecuta en una nueva ventana
        subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', f"{command}; bash -c 'read -p \"Presiona enter para cerrar...\"'"])

