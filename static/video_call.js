
const APP_ID = '3e7cba117dc14b9eb96d8d54c64f9294'
const CHANNEL = sessionStorage.getItem('room')
const TOKEN = sessionStorage.getItem('token')
let UID = Number(sessionStorage.getItem('UID'));

const client = AgoraRTC.createClient({mode:'rtc', codec: 'vp8'})

let localTracks = []
let remoteUsers = {}

let handleUserLeft = async (user) => {
    delete remoteUsers[user.uid]
    document.getElementById(`user-container-${user.uid}`).remove()
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

        let player = document.getElementById(`user-container-${user.uid}`)

        if (player != null)
            player.remove()

        player = `<div class = "video-container" id="user-container-${user.uid}">
                    <div class="username-wrapper"><span class="user-name"  >Hello</span></div>
                    <div class="video-player" id="user-${user.uid}"></div>
                </div>`
        document.getElementById('video-streams').insertAdjacentHTML('beforeend', player)
        user.videoTrack.play(`user-${user.uid}`)
    }
    if(mediaType === 'audio'){
        user.audioTrack.play()
    }
}
let joinAndDisplayLocalStream = async () => {
    client.on('user-published', handleUserJoined)
    client.on('user-left', handleUserLeft)
    try{
        await client.join(APP_ID, CHANNEL, TOKEN, UID)
    }catch(error){
        console.error(error)
    }

    localTracks = await AgoraRTC.createMicrophoneAndCameraTracks()

    let player = `<div class = "video-container" id="user-container-${UID}">
                    <div class="username-wrapper"><span class="user-name"  >Hello</span></div>
                    <div class="video-player" id="user-${UID}"></div>
                </div>`
    document.getElementById('video-streams').insertAdjacentHTML('beforeend', player)
    localTracks[1].play(`user-${UID}`)

    await client.publish([localTracks[0], localTracks[1]])

}

const localVideoDiv1 = document.querySelector('#local-video1')
const localVideoDiv2 = document.querySelector('#local-video2')
const messageList = document.getElementById('message-list')
const sendMessage = document.getElementById('message-send')
const message = document.getElementById('chat-message')

// sendMessage.addEventListener('click', function(){
//     addMessageLocaly(message.value)
//     message.value = ''
// })

function addMessageLocaly(message){
    messageList.insertAdjacentHTML('beforeend',
        `<div class='message'><strong>${call_info['callee_fname']}:</strong> ${message}</div>`
    )
}
joinAndDisplayLocalStream()
document.getElementById('leave-btn').addEventListener('click', leaveAndRemoveLocalStream)
document.getElementById('camera-btn').addEventListener('click', toggleCamera)
document.getElementById('mic-btn').addEventListener('click', toggleMic)
