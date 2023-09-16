import cv2
import numpy as np
import tensorflow as tf
import serial

url='http://192.168.8.115/640x480.jpg'
cap = cv2.VideoCapture(url)

winName = 'IP_CAM'
cv2.namedWindow(winName, cv2.WINDOW_AUTOSIZE)

interpreter = tf.lite.Interpreter(model_path=r'C:\Users\Pc\Desktop\Python\lite-model_movenet_singlepose_lightning_3.tflite')
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
input_shape = input_details[0]['shape']

input_data = np.zeros(input_shape, dtype=np.float32)

assert all(input_dim == dim for input_dim, dim in zip(input_data.shape[1:], input_shape[1:])), "El tamaño del arreglo de entrada no coincide con el tensor de entrada."

while True:
    cap.open(url)
    ret, frame = cap.read()

    resized_frame = cv2.resize(frame, (input_shape[2], input_shape[1]))
    input_data[0] = resized_frame

    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    keypoints = interpreter.get_tensor(output_details[0]['index'])
    
    ii = 0
    posiciones = np.zeros(16)
    posiciones = [6, 8, 10]
    
    centro_x = keypoints[0, 0, 0, 1]  # Coordenada x del punto de referencia
    centro_y = keypoints[0, 0, 0, 0]  # Coordenada y del punto de referencia
    
    puerto = 'COM4' 
    velocidad = 9600  
    ser = serial.Serial(puerto, velocidad)
    if not ser.isOpen():
        ser.open()
    print ('COM4 is open', ser.isOpen())

    for i in range(len(keypoints[0])):
        x = (keypoints[0][i][1] * frame.shape[1])
        y = (keypoints[0][i][0] * frame.shape[0])
        xx=list(map(int,x))
        yy=list(map(int,y))
        datos = [keypoints[0, 0, pos, :] for pos in posiciones]
        valores_x = [(keypoints[0, 0, pos, 1]) for pos in posiciones]
        valores_y = [(keypoints[0, 0, pos, 0]) for pos in posiciones]

        print(valores_x,valores_y)
        print(keypoints[0,0,0,0])
        print(keypoints[0,0,0,1])
        
        #print(datos)
        cv2.circle(frame, (int(valores_x[0]*frame.shape[1]),int(valores_y[0]*frame.shape[0])), 5, (0, 255, 0), -1)
        cv2.circle(frame, (int(valores_x[1]*frame.shape[1]),int(valores_y[1]*frame.shape[0])), 5, (255, 0, 0), -1)
        cv2.circle(frame, (int(valores_x[2]*frame.shape[1]),int(valores_y[2]*frame.shape[0])), 5, (0, 0, 255), -1)
        
        if valores_x[0]-valores_x[1]<= 0.035 and valores_x[0]-valores_x[2]<= 0.035 and valores_y[0]>valores_y[1] and valores_x[1]<valores_x[2]:
            caracter = 'RA.'  # El caracter que deseas enviar
            ser.write(caracter.encode('utf-8'))
            print(caracter)
        #    ser.close()
            
        if valores_x[0]<valores_x[1] and valores_x[1]<valores_x[2] and valores_y[0]-valores_y[1]<= 0.035 and valores_y[1]-valores_y[2]<= 0.035:
            caracter = 'RB.'  # El caracter que deseas enviar
            ser.write(caracter.encode('utf-8'))
            print(caracter)
        #    ser.close()
        
        if valores_x[0]<valores_x[1] and valores_x[1]-valores_x[2]<= 0.035 and valores_y[0]-valores_y[1]<= 0.035 and valores_y[1]<valores_y[2]:
            caracter = 'RC.'  # El caracter que deseas enviar
            ser.write(caracter.encode('utf-8'))
            print(caracter)
        #    ser.close()
            
        if valores_x[0]-valores_x[1]<= 0.035 and valores_x[0]-valores_x[2]<= 0.035 and valores_y[0]>valores_y[1] and valores_x[1]>valores_x[2]:
            caracter = 'RD.'  # El caracter que deseas enviar
            ser.write(caracter.encode('utf-8'))
            print(caracter)
        #    ser.close()
    ser.close()
                  
    cv2.imshow(winName, frame)

    tecla = cv2.waitKey(1) & 0xFF
    if tecla == 27:
        break

cv2.destroyAllWindows()
