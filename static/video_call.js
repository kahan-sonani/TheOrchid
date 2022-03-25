
const APP_ID = '3e7cba117dc14b9eb96d8d54c64f9294'
const CHANNEL = sessionStorage.getItem('room')
const TOKEN = sessionStorage.getItem('token')
let UID = sessionStorage.getItem('uid')

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
        console.log("called")
        // let player = document.getElementById(`user-container-${user.uid}`)
        //
        // if (player != null)
        //     player.remove()
        //
        // player = `<div class = "video-container" id="user-container-${user.uid}">
        //             <div class="username-wrapper"><span class="user-name"  >Hello</span></div>
        //             <div class="video-player" id="user-${user.uid}"></div>
        //         </div>`
        // document.getElementById('video-streams').insertAdjacentHTML('beforeend', player)
        user.videoTrack.play(`user-callee`)
    }
    if(mediaType === 'audio'){
        user.audioTrack.play()
    }
}

let joinAndDisplayLocalStream = async () => {
    // client.on('user-left', handleUserLeft)
    try{
        await client.join(APP_ID, CHANNEL, TOKEN, UID)
    }catch(error){
        console.error(error)
    }

    localTracks = await AgoraRTC.createMicrophoneAndCameraTracks()

    let player = `<div class = "video-container" id="user-container-callee">
                    <div class="username-wrapper"><span class="user-name" >Hello</span></div>
                    <div class="video-player" id="user-callee"></div>
                    <div class = "sub-video-container">
                        <div class="username-wrapper"><span class="user-name" >Hello</span></div>
                        <div class="video-player" id="user-${UID}"></div>
                    </div>
                </div>`
    document.getElementById('video-streams').insertAdjacentHTML('beforeend', player)
    document.getElementById('video-streams')
        .insertAdjacentHTML('beforeend',
            `<div class="window-layout" id="predictions">
                       <h4 class="window-header">ISL Predictions</h4>
                        <hr>
                        <div id="message-list" class="message-list">
                        </div>
                 </div>`)
    localTracks[1].play(`user-${UID}`)
    client.on('user-published', handleUserJoined)

    await client.publish([localTracks[0], localTracks[1]])

    if(enablePredictions.checked)
        document.getElementById('predictions').style.display = 'block'
    else
        document.getElementById('predictions').style.display = 'none'
}

const messageList = document.getElementById('message-list')
const sendMessage = document.getElementById('message-send')
const message = document.getElementById('chat-message')
const enablePredictions = document.getElementById('enable-predictions')

sendMessage.addEventListener('click', function(){
    addMessageLocaly(message.value)
    message.value = ''
})

enablePredictions.addEventListener('change', function (){
    var result;
    if(this.checked) {
        result = 1
        document.getElementById('predictions').style.display = 'block'
    }
    else {
        result = 0
        document.getElementById('predictions').style.display = 'none'
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


function addMessageLocaly(call_info, message){
    messageList.insertAdjacentHTML('beforeend',
        `<div class='message'><strong>${call_info['callee_fname']}:</strong> ${message}</div>`
    )
}
joinAndDisplayLocalStream()
enablePredictions.change()
document.getElementById('leave-btn').addEventListener('click', leaveAndRemoveLocalStream)
document.getElementById('camera-btn').addEventListener('click', toggleCamera)
document.getElementById('mic-btn').addEventListener('click', toggleMic)
