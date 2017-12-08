#!/usr/bin/python2.7

from flask import Flask, render_template, request, jsonify
import thread
import time
import serial
import datetime
import re

import logging



# ================================================ Logging ================================================


logger = logging.getLogger('Boat Software')
hdlr = logging.FileHandler('Boat_Software.log')
formatter = logging.Formatter('%(asctime)s;%(levelname)s;%(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)



# ------------------- End of "Logging" -------------------



# ================================================ Print_Text ================================================

def Print_Text(Print_Prefix, Print_String):


	if "\r\n" in Print_String: # Multiple line taking one at the time

		Print_String_List = Print_String.splitlines()

		while True:

			print time.strftime("%d-%m-%Y %H:%M:%S") + " - " + Print_Prefix + " - " + Print_String_List[0]
			logger.info(Print_Prefix + " - " + Print_String_List[0])

			Print_String_List.remove(Print_String_List[0])

			if not Print_String_List:
				break

	else: # Single line of text no handling needed
		print time.strftime("%d-%m-%Y %H:%M:%S") + " - " + Print_Prefix + " - " + Print_String
		logger.info(Print_Prefix + " - " + Print_String)



# ------------------- End of "Print_Text" -------------------




# ================================================ Global Veriables ================================================


Software_version = "Software version 0.10"
Print_Text('Boat software - ' + Software_version, 'Starting')
logger.info('Boat software - ' + Software_version + ' Starting')

Command_Queue = ''

Relay_State_Dictionary = {}

Voltmeter_State_Dictionary = {}

# Relay_State_Dictionary['Relay_Changed'] = 'NO'






# ------------------------------------------------ Cron ------------------------------------------------

Cron_Interval = 1800 # Cron interval time in secounds


# ------------------------------------------------ Serial Interface ------------------------------------------------
# ------------------------------------------------ Web Server------------------------------------------------

app = Flask(__name__)


def Cron_Jobs( ):

	global Command_Queue

	while True:
		Print_Text('Cron Job', 'Voltmeter 1')
		Command_Queue = Command_Queue + "voltmeter 1;"

		Print_Text('Cron Job', 'Relay All State')
		Command_Queue = Command_Queue + "relay all state;"

		time.sleep(int(Cron_Interval))
# ------------------- End of "Cron_Jobs" -------------------



def Serial_Interface( ):

	Serial_Interface_Started = False

	if Serial_Interface_Started == False:

		Serial_Interface_Started = True

		ser = serial.Serial('/dev/ttyACM0', 115200, timeout=10) # CHANEG ME
		# ser = serial.Serial('COM20', 115200, timeout=10)

		def Serial_Write( ):

			global Command_Queue

			Command = Command_Queue.split(';')[0]

			Command = Command_Queue.split(';')[0]

			if len(Command) == 0:
				return

			Print_Text('Serial Interface - Send', Command)

			Command_Queue = Command_Queue.replace(Command + ";", '')

			ser.write(Command)
			Serial_Read()
			return
	# ------------------- End of "Serial_Write" -------------------

		def Serial_Read( ):

			while True: # Read loop to make sure that all text is read
				time.sleep(0.6)
				bytesToRead = ser.inWaiting()

				if (bytesToRead == 0):
					break

				Serial_Data = ser.read(bytesToRead)


# -------------------------------------- Relay State --------------------------------------
				if "State is" in Serial_Data:
					if "Relay Number" in Serial_Data:

						for item in Serial_Data.split("\r\n"): # Finds the line with "State is" aka answer from the unit aka current state

							if "State is" in item:

								State_Is = item.strip()

								Relay_State_Number = State_Is.replace('Relay Number ', '')
								Relay_State_Number = Relay_State_Number.replace(' State is ', '')
								Relay_State_Number = Relay_State_Number.replace('ON', '')
								Relay_State_Number = Relay_State_Number.replace('OFF', '')

								try:
									if 'ON' in State_Is:
										Relay_State_Dictionary['Relay_' + str(Relay_State_Number)] = 'C-ON'

									elif 'OFF' in State_Is:
										Relay_State_Dictionary['Relay_' + str(Relay_State_Number)] = 'C-OFF'

								except KeyError:
									if 'ON' in State_Is:
										Relay_State_Dictionary['Relay_' + str(Relay_State_Number)] = 'C-ON'

									elif 'OFF' in State_Is:
										Relay_State_Dictionary['Relay_' + str(Relay_State_Number)] = 'C-OFF'
# -------------------------------------- Relay State - End --------------------------------------




# -------------------------------------- Voltmeter --------------------------------------
				if " Value: " in Serial_Data:
					if "Voltmeter Number " in Serial_Data:

						for item in Serial_Data.split("\r\n"): # Finds the line with "State is" aka answer from the unit aka current state

							if " Value: " in item:

								State_Is = item.strip()

								Voltmeter_Number = State_Is.replace('Voltmeter Number ', '')
								Voltmeter_Number = Voltmeter_Number[:Voltmeter_Number.index(' Value:')]


								Voltmeter_Value = State_Is.replace('Voltmeter Number ', '')
								Voltmeter_Value = Voltmeter_Value[Voltmeter_Value.index(' Value:'):]
								Voltmeter_Value = Voltmeter_Value[8:]


								Voltmeter_Update_Time = time.strftime("%H:%M:%S %d-%m-%Y")

								Voltmeter_State_Dictionary['Voltmeter_' + str(Voltmeter_Number)] = "C-" + Voltmeter_Value + ";" + Voltmeter_Update_Time

				Print_Text('Serial Interface - Receive', Serial_Data)


# -------------------------------------- Voltmeter - End --------------------------------------






# ------------------- End of "Serial_Read" -------------------

		while True:
			Serial_Read()

			Serial_Write()

			time.sleep(0.5)
# ------------------- End of "Serial Interface" -------------------


def Web_Server( ):

	Flask_Started = False

	if Flask_Started == False:

		Flask_Started = True

		if __name__ == '__main__':
			# app.run(host='0.0.0.0', port=80, debug=False, threaded=True)
			app.run(host='0.0.0.0', port=8182, debug=False)
# ------------------- End of "Web Server" -------------------



@app.route('/')
def index():

	return render_template('main.html')
# ------------------- End of "/" -------------------



@app.route('/Refresh_Function')
def Refresh_Function():

	x = 1

	Refresh_Function_Entry = ''
	Refresh_Function_Value = ''
	Refresh_Function_Color = ''

	while True:

		try:
			if Relay_State_Dictionary['Relay_' + str(x)] == 'ON':
				Color = 'green'

			elif Relay_State_Dictionary['Relay_' + str(x)] == 'OFF':
				Color = 'red'

			else:
				Color = '#B4ACBA'

			Refresh_Function_Entry = Refresh_Function_Entry + 'T1N' + str(x) + "---"
			Refresh_Function_Value = Refresh_Function_Value + Relay_State_Dictionary['Relay_' + str(x)] + "---"
			Refresh_Function_Color = Refresh_Function_Color + Color + "---"

		except KeyError:
			break

		x += 1

	return jsonify(Refresh_Function_Entry=Refresh_Function_Entry, Refresh_Function_Value=Refresh_Function_Value, Refresh_Function_Color=Refresh_Function_Color)
# ------------------- End of "Refresh_Function" -------------------



@app.route('/background_process_Auto_Refresh')
def background_process_Auto_Refresh():

# ------------------- Update Relay State -------------------
	if 'C-' in str(Relay_State_Dictionary):

		x = 1

		Return_Multiple_Hits_Entry = ''
		Return_Multiple_Hits_Value = ''
		Return_Multiple_Hits_Color = ''

		Return_Multiple_Hits = False

		while True:

			try:
				if 'C-' in Relay_State_Dictionary['Relay_' + str(x)]:

					if 'C-' in str(Relay_State_Dictionary):

						Change_Marker = True

					Relay_State_Dictionary['Relay_' + str(x)] = Relay_State_Dictionary['Relay_' + str(x)][2:]

					if Relay_State_Dictionary['Relay_' + str(x)] == 'ON':
						Color = 'green'
					else:
						Color = 'red'


					if 'C-' in str(Relay_State_Dictionary):
						Return_Multiple_Hits_Entry = Return_Multiple_Hits_Entry + 'T1N' + str(x) + "---"
						Return_Multiple_Hits_Value = Return_Multiple_Hits_Value + Relay_State_Dictionary['Relay_' + str(x)] + "---"
						Return_Multiple_Hits_Color = Return_Multiple_Hits_Color + Color + "---"

						Return_Multiple_Hits = True

						Change_Marker = False


					elif (Return_Multiple_Hits == False):

						return jsonify(Return_Entry_Auto_Refresh=('T1N' + str(x)), Return_Value_Auto_Refresh=Relay_State_Dictionary['Relay_' + str(x)], Return_Color_Auto_Refresh=Color, Return_Multiple_Hits_Auto_Refresh=False)


					elif (Return_Multiple_Hits == True) and (Change_Marker == True):
						Return_Multiple_Hits_Entry = Return_Multiple_Hits_Entry + 'T1N' + str(x) + "---"
						Return_Multiple_Hits_Value = Return_Multiple_Hits_Value + Relay_State_Dictionary['Relay_' + str(x)] + "---"
						Return_Multiple_Hits_Color = Return_Multiple_Hits_Color + Color + "---"

						return jsonify(Return_Entry_Auto_Refresh=Return_Multiple_Hits_Entry, Return_Value_Auto_Refresh=Return_Multiple_Hits_Value, Return_Color_Auto_Refresh=Return_Multiple_Hits_Color, Return_Multiple_Hits_Auto_Refresh=True)






			except KeyError:
				break

			x += 1

# ------------------- Update Voltmeter State -------------------
	elif 'C-' in str(Voltmeter_State_Dictionary):

		x = 1

		Return_Multiple_Hits_Entry = ''
		Return_Multiple_Hits_Value = ''
		Return_Multiple_Hits_Color = ''

		Return_Multiple_Hits = False

		while True:

			try:
				if 'C-' in Voltmeter_State_Dictionary['Voltmeter_' + str(x)]:

					if 'C-' in str(Voltmeter_State_Dictionary):

						Change_Marker = True

					Voltmeter_State_Dictionary['Voltmeter_' + str(x)] = Voltmeter_State_Dictionary['Voltmeter_' + str(x)][2:]


					if float(Voltmeter_State_Dictionary['Voltmeter_' + str(x)][:5]) > 12.10:
						Color = "green"

					else:
						Color = "red"


					if 'C-' in str(Voltmeter_State_Dictionary): # Multiple changes
						Return_Multiple_Hits_Entry = Return_Multiple_Hits_Entry + 'T51N' + str(x) + "V2" + "---"
						Return_Multiple_Hits_Value = Return_Multiple_Hits_Value + Voltmeter_State_Dictionary['Voltmeter_' + str(x)] + "---"
						Return_Multiple_Hits_Color = Return_Multiple_Hits_Color + Color + "---"

						Return_Multiple_Hits = True

						Change_Marker = False


					elif (Return_Multiple_Hits == False): # Single cange

						return jsonify(Return_Entry_Auto_Refresh=('T51N' + str(x) + 'V2---' + 'T51N' + str(x) + 'V2TD---'), Return_Value_Auto_Refresh=Voltmeter_State_Dictionary['Voltmeter_' + str(x)].replace(';', "---", 1) + "---", Return_Color_Auto_Refresh=Color + '---' + Color + '---', Return_Multiple_Hits_Auto_Refresh=True)


					elif (Return_Multiple_Hits == True) and (Change_Marker == True):
						Return_Multiple_Hits_Entry = Return_Multiple_Hits_Entry + 'T51N' + str(x) + "V2" + "---"
						Return_Multiple_Hits_Value = Return_Multiple_Hits_Value + Voltmeter_State_Dictionary['Voltmeter_' + str(x)] + "---"
						Return_Multiple_Hits_Color = Return_Multiple_Hits_Color + Return_Multiple_Hits_Color + "---"

						return jsonify(Return_Entry_Auto_Refresh=Return_Multiple_Hits_Entry, Return_Value_Auto_Refresh=Return_Multiple_Hits_Value, Return_Color_Auto_Refresh=Return_Multiple_Hits_Color, Return_Multiple_Hits_Auto_Refresh=True)






			except KeyError:
				break

			x += 1

	else:
		return jsonify(Return_Entry_Auto_Refresh="NothingToReport", Return_Value_Auto_Refresh="NothingToReport", Return_Color_Auto_Refresh="NothingToReport")
# ------------------- End of "background_process_Auto_Refresh" -------------------


@app.route('/Main_Function')
def Button_Multiple_Actions():

	global Command_Queue

	Relay_Return_Color = '#B4ACBA'

	try:

		Main_Function_Send_Value = request.args.get('Main_Function_Send_Value', 0, type=str)

		if "RedWhiteLight" in Main_Function_Send_Value: # Red / White lights

			if (Relay_State_Dictionary['Relay_2'] == "OFF") and (Relay_State_Dictionary['Relay_3'] == "OFF"): # Both Off turn off RED

				Command_Queue =  Translator("T1N3V1;")

			elif (Relay_State_Dictionary['Relay_2'] == "ON") and (Relay_State_Dictionary['Relay_3'] == "OFF"): # White ON = Red ON - White OFF

				Command_Queue =  Translator("T1N3V1;T1N2V2;")

			elif (Relay_State_Dictionary['Relay_2'] == "OFF") and (Relay_State_Dictionary['Relay_3'] == "ON"): # White OFF = Red ON - White OFF

				Command_Queue =  Translator("T1N2V1;T1N3V2;")

			return jsonify(Return_Entry="Done")


		if "GeneratorInverter" in Main_Function_Send_Value: # Generator / Inverter

			if (Relay_State_Dictionary['Relay_7'] == "OFF") and (Relay_State_Dictionary['Relay_8'] == "OFF"): # ON

				Command_Queue =  Translator("T1N7V1;T1N8V1;")

			elif (Relay_State_Dictionary['Relay_7'] == "ON") and (Relay_State_Dictionary['Relay_8'] == "ON"): # OFF

				Command_Queue =  Translator("T1N7V2;T1N8V2;")

			return jsonify(Return_Entry="Done")





		elif "T1N" in Main_Function_Send_Value:

			Command_Queue =  Translator(Main_Function_Send_Value.replace('---', ";")) + ";"

			# Command_Queue = Translator(Main_Function_Send_Value) + ";"

			return jsonify(Return_Entry="Done")


	except Exception as e:
		logger.error("Button_Relay generated and error")
		print "HORRIBLE ERROR"
		return jsonify(Return_Entry="ERROR: " + str(e))
# ------------------- End of "Button_Multiple_Actions" -------------------

@app.route('/Button_Relay')
def Button_Relay():

	global Command_Queue

	Relay_Return_Color = '#B4ACBA'

	try:

		Relay_Button_Send_Value = request.args.get('Relay_Button_Send_Value', 0, type=str)

		if "T1N" in Relay_Button_Send_Value:

			Command_Queue = Translator(Relay_Button_Send_Value) + ";"

			return jsonify(Return_Entry="Done")


	except Exception as e:
		logger.error("Button_Relay generated and error")
		print "HORRIBLE ERROR"
		return jsonify(Return_Entry="ERROR: " + str(e))
# ------------------- End of "Button_Relay" -------------------


@app.route('/Button_Voltmeter')
def Button_Voltmeter():

	global Command_Queue

	Voltmeter_Return_Color = '#B4ACBA'

	try:
		Voltmeter_Button_Send_Value = request.args.get('Voltmeter_Button_Send_Value', 0, type=str)

		if "T51N" in Voltmeter_Button_Send_Value:

			Command_Queue = Translator(Voltmeter_Button_Send_Value) + ";"

			return jsonify(Return_Entry="Done")


	except Exception as e:
		print "HORRIBLE ERROR"
		return jsonify(Return_Entry="ERROR: " + str(e))
# ------------------- End of "Button_Voltmeter" -------------------



def Translator(Translator_String):

	if "T1N" in Translator_String:

		Translator_String = Translator_String.replace('T1N', 'relay ')

		Translator_String = Translator_String.replace('V1', ' on')
		Translator_String = Translator_String.replace('V2', ' off')
		Translator_String = Translator_String.replace('V3', ' state')


	elif "T51N" in Translator_String:

		Translator_String = Translator_String.replace('T51N', 'voltmeter ')

		Translator_String = Translator_String.replace('V1', '')

	return Translator_String
# ------------------- End of "Translator" -------------------


# ================================================ Thread's ================================================
try:
   thread.start_new_thread( Cron_Jobs, () )
   thread.start_new_thread( Serial_Interface, () )
   thread.start_new_thread( Web_Server, () )
except:
   print "Error: unable to start thread"
   logger.error("Error: unable to start thread")


while 1:
   pass
