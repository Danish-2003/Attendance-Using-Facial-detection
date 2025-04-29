from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.utils import timezone
import numpy as np
import pickle as pkl
import cv2
from mtcnn import MTCNN
from deepface import DeepFace
from datetime import datetime
from scipy.spatial.distance import cosine
from home.models import *

detector = MTCNN()

# Create your views here.
def home(request):  # sourcery skip: last-if-guard
    context = {'page':'Home'}
    if request.method == 'POST' and request.FILES.get("image"):
        data = request.POST

        name = data.get("name")
        roll_no = data.get("roll_no")
        uploaded_image = request.FILES.get("image")

        image_array = np.frombuffer(uploaded_image.read(),np.uint8)



        img = cv2.imdecode(image_array,cv2.IMREAD_COLOR)

        img = cv2.resize(img,(500,500))

        face = detector.detect_faces(img)

        if not face:
            return JsonResponse({"message" : "No Face Found" },status=400)
        
        x,y,w,h = face[0]["box"]

        stud_face = img[y:y+h, x:x+w]

        embedding = DeepFace.represent(stud_face,model_name="Facenet",enforce_detection=False)

        if not embedding:
            return JsonResponse({"message": "Face Extraction Failed "},status=400)

        face_embedding = pkl.dumps(np.array(embedding[0]["embedding"]))


        Students.objects.create(
            name = name,
            roll_no = roll_no,
            face_embeddings = face_embedding,
            image = uploaded_image,
        )

        return redirect('/')


    return render(request,"index.html",context)




def attendance(request):
    # sourcery skip: extract-method, remove-redundant-fstring, remove-unnecessary-else, swap-if-else-branches
    context = {}
    if request.method == 'POST' and request.FILES.get("image"):
        uploaded_image = request.FILES.get("image")

        image_array = np.frombuffer(uploaded_image.read(),np.uint8)

        img = cv2.imdecode(image_array,cv2.IMREAD_COLOR)

        img = cv2.resize(img,(500,500))


        face_detect = detector.detect_faces(img)

        if not face_detect : 
            return JsonResponse({"message": "No face Detected"},status=400)

        x,y,w,h = face_detect[0]["box"]

        face = img[y:y+h,x:x+w]

        test_embedding = DeepFace.represent(face,model_name="Facenet",enforce_detection=False)

        if not test_embedding:
            return JsonResponse({"message": "Face Extraction Failed "},status=400)

        test_embedding = np.array(test_embedding[0]["embedding"])    


        students = Students.objects.all()
        recognized_stud = None
        min_distance = float("inf")

        for student in students:
            stored_emb = pkl.loads(student.face_embeddings)

            distance = cosine(test_embedding, stored_emb)

            if distance < min_distance and distance < 0.4:
                min_distance = distance
                recognized_stud = student

            if recognized_stud:
                context = {"name": recognized_stud.name,"image" :recognized_stud.image,"page":"attendance"}

                today = timezone.now().date()
                attendance,created = Attendance.objects.get_or_create(student = recognized_stud,date = today)

                if created :
                    return JsonResponse({"Message": f"Attendance marked for {recognized_stud.name}"})
                else:
                    return JsonResponse({"Message":f"Attendance is already marked "})


            


    return render(request,"attendance.html",context)