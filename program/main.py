import classes
import cv2
import threading


# Memulai stream video
video_stream = classes.VideoStream().start() # pada tanda kurung VideoStream() masukkan IP adress dari kamera cctv
video_stream2 = classes.VideoStream(1).start() # perbanyak variabel video_stream sesuai dengan kamera yang digunakan 

# Memulai persiapan deteksi truck dan OCR
ocr = classes.OCR().start()
truckdetection = classes.TruckDetection().start()

# Perintah untuk melakukan pemberian hasil stream kepada OCR dan truckdetection
ocr.set_exchange([video_stream,video_stream2]) # semua variabel video stream di masukkan kedalam []
truckdetection.set_exchange([video_stream,video_stream2]) # semua variabel video stream di masukkan kedalam []

# uncoment jika ingin melihat berapa thread yang digunakan
# print("Active threads: {}".format(threading.activeCount()))

while True:
    frame1 = video_stream.frame
    frame2 = video_stream2.frame
    # uncomment jika tidak ingin melihat hasil stream
    cv2.imshow("OCR Realtime",frame1) # untuk melihat hasil stream pada video_stream
    cv2.imshow("OCR Realtime2",frame2) # untuk melihat hasil stream pada video_stream2

    pressed_key = cv2.waitKey(1) & 0xFF
    if pressed_key == ord('q'): # menghentikan proses deteksi dengan menekan huruf q pada keyboard
        ###
        # Tambahkan jumlah video_stream.stop_process sesuai dengan jumlah variabel video_stream yang dibuat diatas
        # ###
        video_stream.stop_process() # untuk menghentikan video stream
        video_stream2.stop_process() # untuk menghentikan video stream


        ocr.stop_process()
        truckdetection.stop_process()
        break

cv2.destroyAllWindows()
