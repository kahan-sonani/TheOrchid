
const APP_ID = '3e7cba117dc14b9eb96d8d54c64f9294'
const CHANNEL = sessionStorage.getItem('room')
const TOKEN = sessionStorage.getItem('token')
let UID = parseInt(sessionStorage.getItem('UID'))

const client = AgoraRTC.createClient({mode:'rtc', codec: 'vp8'})

let localTracks = []
let remoteUsers = {}

function process_landmarks(landmarks) {
        let x_list = [], y_list = []
        let i = 0;
        for(; i < 21; i++) {
            x_list.push(landmarks[i].x)
            y_list.push(landmarks[i].y)
        }
        return [x_list, y_list]
    }

    function process_pose_landmarks(landmarks) {
        let x_list = [], y_list = []
        let i = 0
        for(;i < 25;i++) {
            x_list.push(landmarks[i].x)
            y_list.push(landmarks[i].y)
        }
        return [x_list, y_list]
    }

    function process_pose_keypoints(results){
        let pose = process_pose_landmarks(results.poseLandmarks)
        let pose_x = pose[0]
        let pose_y = pose[1]
        return [pose_x, pose_y]
    }

    function swap_hands(left_wrist, right_wrist, hand, input_hand) {
        let left_wrist_x = left_wrist[0], left_wrist_y = left_wrist[1]
        let right_wrist_x = right_wrist[0], right_wrist_y = right_wrist[1]
        let hand_x = hand[0], hand_y = hand[1]

        let left_dist = (left_wrist_x - hand_x) ** 2 + (left_wrist_y - hand_y) ** 2
        let right_dist = (right_wrist_x - hand_x) ** 2 + (right_wrist_y - hand_y) ** 2

        if(left_dist < right_dist && input_hand === "h2")
            return true

        if(right_dist < left_dist && input_hand === "h1")
            return true
        return false
    }

    function process_hand_keypoints(results) {
        let hand1_x = [], hand1_y = [], hand2_x = [], hand2_y = []

        if(results.multiHandLandmarks !== null) {
            if(results.multiHandLandmarks.length > 0) {
                let hand1 = results.multiHandLandmarks[0]
                let hands = process_landmarks(hand1)
                hand1_x = hands[0]
                hand1_y = hands[1]
            }

            if(results.multiHandLandmarks > 1) {
                let hand2 = results.multiHandLandmarks[1]
                let hands = process_landmarks(hand2)
                hand2_x = hands[0]
                hand2_y = hands[1]
            }
        }

        return [hand1_x, hand1_y, hand2_x, hand2_y]
    }

let leaveAndRemoveLocalStream = async () =>{
    for (let i = 0; localTracks.length > i; i++){
        localTracks[i].stop()
        localTracks[i].close()
    }

    await client.leave()
    window.open('/home', '_self')
}

let toggleCamera = async (e)=> {
    if(localTracks[1].muted){
        await localTracks[1].setMuted(false)
        e.target.style.backgroundColor = '#fff'
    }else{
        await localTracks[1].setMuted(true)
        e.target.style.backgroundColor = 'rgb(255,80,80,1)'
    }
}

let toggleMic = async (e)=> {
    if(localTracks[0].muted){
        await localTracks[0].setMuted(false)
        e.target.style.backgroundColor = '#fff'
    }else{
        await localTracks[0].setMuted(true)
        e.target.style.backgroundColor = 'rgb(255,80,80,1)'
    }
}

let handleUserJoined = async (user, mediaType) => {
    remoteUsers[user.uid] = user
    await client.subscribe(user, mediaType)
    if (mediaType === 'video'){

        await user.videoTrack.play(`user-callee`)
        document.getElementById('user-name-callee').textContent = other_user_fname

    }
    if(mediaType === 'audio'){
        await user.audioTrack.play()
    }
}
let startMonitor = -1
let n_frames = 0
let sequence = 0

let joinAndDisplayLocalStream = async () => {

    client.on('user-published', handleUserJoined)
    try{
        await client.join(APP_ID, CHANNEL, TOKEN, UID)
    }catch(error){
        console.error(error)
    }

    let pose_points_x = [], pose_points_y = []
    let hand1_points_x = [], hand1_points_y = []
    let hand2_points_x = [], hand2_points_y = []
    //let uid = random.randint(1, 100)

    function onHandsResults(results) {
        if(startMonitor === 1) {
            let hands = process_hand_keypoints(results)
            let hand1_x = hands[0]
            let hand1_y = hands[1]
            let hand2_x = hands[2]
            let hand2_y = hands[3]
            console.log(`hands: ${pose_points_x[pose_points_x.length - 1]}`)
            if(hand1_x.length > 0 && hand2_x.length === 0)
            {
                console.log("pose_points_x")
                if(swap_hands([pose_points_x[pose_points_x.length - 1][15], pose_points_y[pose_points_y.length - 1][15]],[pose_points_x[pose_points_x.length - 1][16], pose_points_y[pose_points_y.length - 1][16]], [hand1_x[0], hand1_y[0]],"h1"))
                    [hand1_x, hand1_y, hand2_x, hand2_y] = [hand2_x, hand2_y, hand1_x, hand1_y]
            }
            else if (hand1_x.length === 0 && hand2_x.length > 0)
                if(swap_hands([pose_points_x[pose_points_x.length - 1][15], pose_points_y[pose_points_y.length - 1][15]],[pose_points_x[pose_points_x.length - 1][16], pose_points_y[pose_points_y.length - 1][16]], [hand2_x[0], hand2_y[0]],"h2"))
                    [hand1_x, hand1_y, hand2_x, hand2_y] = [hand2_x, hand2_y, hand1_x, hand1_y]

            hand1_x = (hand1_x.length !== 0) ? hand1_x : Array(21).fill(Number.NaN)
            hand1_y = (hand1_y.length !== 0) ? hand1_y : Array(21).fill(Number.NaN)
            hand2_x = (hand2_x.length !== 0) ? hand2_x : Array(21).fill(Number.NaN)
            hand2_y = (hand2_y.length !== 0) ? hand2_y : Array(21).fill(Number.NaN)

            hand1_points_x.push(hand1_x)
            hand1_points_y.push(hand1_y)
            hand2_points_x.push(hand2_x)
            hand2_points_y.push(hand2_y)

        }
    }

    function onPoseResults(results){
        if(startMonitor === 1) {
            let pose = process_pose_keypoints(results)
            let pose_x = pose[0]
            let pose_y = pose[1]
            console.log(`pose: ${pose_x}`)
            pose_x = (pose_x.length !== 0) ? pose_x : Array(25).fill(Number.NaN)
            pose_y = (pose_y.length !== 0) ? pose_y : Array(25).fill(Number.NaN)
            pose_points_x.push(pose_x)
            pose_points_y.push(pose_y)
            n_frames += 1
        }
        else if (startMonitor === 0){
            console.log("Saving keypoints to temp.json file...")
            let id;
            if(!edit_mode)
                id = sequence++
            else
                id = edit_uid
            let save_data = {
                "uid": id,
                "label": id,
                "hand1_x": hand1_points_x,
                "hand1_y": hand1_points_y,
                "hand2_x": hand2_points_x,
                "hand2_y": hand2_points_y,
                "pose_x": pose_points_x,
                "pose_y": pose_points_y,
                "n_frames": n_frames,
            }
            postVideoKeypoints(save_data)
            startMonitor = -1
        }
    }

    const pose = new Pose({locateFile: (file) => {
      return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
    }});

    pose.setOptions({
      modelComplexity: 1,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5
    });

    const hands = new Hands({locateFile: (file) => {
      return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
    }});

    hands.setOptions({
      maxNumHands: 2,
      modelComplexity: 1,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5
    });

    hands.onResults(onHandsResults);
    pose.onResults(onPoseResults);

    video_local = document.getElementById('video_track_local');
    camera = new Camera(video_local, {
      onFrame: async () => {
          await hands.send({image: video_local})
          await pose.send({image: video_local})
      },
      width: 640,
      height: 480
    });

    camera.start();
    localTracks[0] = await AgoraRTC.createMicrophoneAudioTrack()
    localTracks[1] = AgoraRTC.createCustomVideoTrack({mediaStreamTrack: camera.g.getVideoTracks()[0]})

    if(enablePredictions.checked)
        document.onkeydown = recEvent
    if(enablePredictions.checked)
        recognition.start()

    document.getElementById('user-name-caller').textContent = user_fname
    await client.publish([localTracks[0], localTracks[1]])

}

function recEvent(event) {
        event = event || window.events[0]
        if(event.altKey && event.key === "s"){
            updateRecordStatus()
        }
}

const messageList = document.getElementById('message-list')
const sendMessage = document.getElementById('message-send')
const message = document.getElementById('chat-message')
const enablePredictions = document.getElementById('enable-predictions')
const other_user_fname = sessionStorage.getItem('other_user_fname')
const other_user_phone = sessionStorage.getItem('other_user_phone')
const user_fname = sessionStorage.getItem('fname')
const recordUI = document.getElementById('start-record')
const predictionList = document.getElementById('prediction-list')
const predictionModal = document.getElementById('predictionModal')
const closePred = document.getElementById('close-pred')
const editPred = document.getElementById('edit-pred')
const deletePred = document.getElementById('delete-pred')
const sequencePred = document.getElementById('sequence')
const labelPred = document.getElementById('label')
const predSend = document.getElementById('pred-send')
const enableTranscription = document.getElementById('enable-speech-to-text')

window.SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
let finalTranscript = '';
let recognition = new window.SpeechRecognition();
recognition.interimResults = true;
recognition.maxAlternatives = 10;
recognition.continuous = true;
recognition.onresult = (event) => {
      let interimTranscript = '';
      for (let i = event.resultIndex, len = event.results.length; i < len; i++) {
        let transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }
      message.value = finalTranscript + interimTranscript;
    }

recognition.onspeechend = function() {
    finalTranscript = ''
    recognition.start();
}

var predictions = {}

var edit_mode = false
var edit_uid;
var camera;
var rec = false

predSend.addEventListener('click', function (){

    let response = {}
    response['code'] = PREDICTIONS
    response['other_user_phone'] = other_user_phone
    response['predictions'] = JSON.stringify(predictions)
    websocket.send(JSON.stringify(response))
    predictions = {}
    predictionList.innerHTML = ''
})
closePred.addEventListener('click', function (){
    predictionModal.style.display = 'none'
})

editPred.addEventListener('click', function(){
    predictionModal.style.display = 'none'
    updateRecordStatus()
    edit_mode = true
})

function updateRecordStatus(){
    rec = !rec
    if(startMonitor === -1)
        startMonitor = 1
    else if(startMonitor === 0)
        startMonitor = 1
    else
        startMonitor = 0
    if(rec) {
        recordUI.style.display = 'block'
    }
    else
        recordUI.style.display = 'none'
}


sendMessage.addEventListener('click', function(){
    if(message.value !== '') {
        addMessageLocally()
        response = {}
        response['code'] = CHAT_MESSAGE
        response['other_user_phone'] = other_user_phone
        response['user_fname'] = user_fname
        response['message'] = message.value
        websocket.send(JSON.stringify(response))
        message.value = ''
    }

})

function addPredictionLocally(response) {
    predictionList.insertAdjacentHTML('beforeend', `<a id="${response['uid']}" onclick="showModal(${response['uid']}, '${response['predicted_label']}');" style="margin-left: 5px;" class="link-white">${response['predicted_label']}</a>`)
}

function editPredictionLocally(response) {
    let pred = document.getElementById(`${response['uid']}`)
    pred.innerHTML = response['predicted_label']
}

function openPredictionInfo(uid, label) {
    predictionModal.style.display = 'block'
    edit_uid = uid
    sequencePred.textContent = `Sequence: ${uid}`
    labelPred.textContent = `Label: ${label}`

    deletePred.addEventListener('click', function(){
        predictionModal.style.display = 'none'
        document.getElementById(`${uid}`).remove()
        delete predictions[`${uid}`]
    })
}

function showModal(uid, label){
    openPredictionInfo(uid, label)
}

function postVideoKeypoints(data){
    $.ajax({
        type: "POST",
        url: 'inference',
        data: {
            key_points: JSON.stringify(data),
        },
        success: function callback(response){
            predictions[`${response['uid']}`] = response['predicted_label']
            if(!edit_mode)
                addPredictionLocally(response)
            else {
                edit_mode = false
                editPredictionLocally(response)
            }
        },
        error : function(e) {
            console.log(e)
        }
    })
}

enableTranscription.addEventListener('change', function(){
    var result;
    if(this.checked){
        result = 1
        recognition.start()
    }else{
        result = 0
        recognition.stop()
    }
    $.ajax({
        type: "POST",
        url: 'enableTranscription',
        data: {
            enable_transcriptions: `${result}`
        },
        success: function callback(response){
            console.log(response.result);
        }
    })
})

enablePredictions.addEventListener('change', function (){
    var result;
    if(this.checked) {
        result = 1
        document.onkeydown = recEvent
    }
    else {
        result = 0
        document.onkeydown = null
    }

    $.ajax({
        type: "POST",
        url: 'enablePredictions',
        data: {
            enable_predictions: `${result}`
        },
        success: function callback(response){
            console.log(response.result);
        }
    })
})

function addRemoteMessageFromCaller(data){
    messageList.insertAdjacentHTML('beforeend',
        `<div class='message'><strong>${data['user_fname']}:</strong> ${data['message']}</div>`
    )
}

function addPredictionsFromRemoteCaller(data){
    predictionList.insertAdjacentHTML('beforeend', data['predictions'])
}

function addMessageLocally(){
    messageList.insertAdjacentHTML('beforeend',
        `<div class='message'><strong>You:</strong> ${message.value}</div>`
    )
}

joinAndDisplayLocalStream()
document.getElementById('leave-btn').addEventListener('click', leaveAndRemoveLocalStream)
document.getElementById('camera-btn').addEventListener('click', toggleCamera)
document.getElementById('mic-btn').addEventListener('click', toggleMic)