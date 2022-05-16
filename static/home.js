var modal = document.getElementById('myModal')
var onCallFromHome = document.getElementById('startFromHome')
var closeModal = document.getElementById('close')
var callInput = document.getElementById('call-1a20')
var timer = document.getElementById('timer')
var timer_div = document.getElementById('timer-div')
var person = document.getElementById('person')
var phones = document.getElementById('phones')
var callTimer = null


closeModal.addEventListener("click", function(){
    callTimeout(true)
    person.style.display = 'block'
    phones.style.display = 'block'
})

onCallFromHome.addEventListener("click", function(){
    modal.style.display = 'block'
    person.style.display = 'none'
    phones.style.display = 'none'
    callRequestLoading(callInput.value)
}, false)


