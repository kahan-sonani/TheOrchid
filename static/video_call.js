
const APP_ID = '3e7cba117dc14b9eb96d8d54c64f9294'
const CHANNEL = sessionStorage.getItem('room')
const TOKEN = sessionStorage.getItem('token')
let UID = parseInt(sessionStorage.getItem('UID'))

const client = AgoraRTC.createClient({mode:'rtc', codec: 'vp8'})

let localTracks = []
let remoteUsers = {}

// let handleUserLeft = async (user) => {
//     delete remoteUsers[user.uid]
//     document.getElementById(`user-container-`).remove()
// }

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

let joinAndDisplayLocalStream = async () => {
    client.on('user-published', handleUserJoined)
    try{
        await client.join(APP_ID, CHANNEL, TOKEN, UID)
    }catch(error){
        console.error(error)
    }

    localTracks = await AgoraRTC.createMicrophoneAndCameraTracks()
    await localTracks[1].play(`user-caller`)
    document.getElementById('user-name-caller').textContent = user_fname
    await client.publish([localTracks[0], localTracks[1]])

    if(enablePredictions.checked)
        document.getElementById('predictions').style.visibility = 'visible'
    else
        document.getElementById('predictions').style.visibility = 'hidden'
}

const messageList = document.getElementById('message-list')
const sendMessage = document.getElementById('message-send')
const message = document.getElementById('chat-message')
const enablePredictions = document.getElementById('enable-predictions')
const other_user_fname = sessionStorage.getItem('other_user_fname')
const other_user_phone = sessionStorage.getItem('other_user_phone')
const user_fname = sessionStorage.getItem('fname')
const recordUI = document.getElementById('start-record')
var rec = false


document.onkeydown = function (event) {
    event = event || window.events[0]
    if(event.altKey && event.key === "s"){
        rec = !rec

        if(rec)
            recordUI.style.display = 'block'
        else
            recordUI.style.display = 'none'
    }
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

enablePredictions.addEventListener('change', function (){
    var result;
    if(this.checked) {
        result = 1
        document.getElementById('predictions').style.visibility = 'visible'
    }
    else {
        result = 0
        document.getElementById('predictions').style.visibility = 'hidden'
    }

    $.ajax({
        type: "POST",
        url: 'saveCallSettings',
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

function addMessageLocally(){
    messageList.insertAdjacentHTML('beforeend',
        `<div class='message'><strong>You:</strong> ${message.value}</div>`
    )
}

joinAndDisplayLocalStream()
document.getElementById('leave-btn').addEventListener('click', leaveAndRemoveLocalStream)
document.getElementById('camera-btn').addEventListener('click', toggleCamera)
document.getElementById('mic-btn').addEventListener('click', toggleMic)