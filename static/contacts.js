
      // Client ID and API key from the Developer Console
      var CLIENT_ID = '456816466000-fllno6mknd0nq7fivp486gkd7f35g00f';
      var API_KEY = 'AIzaSyCMTx5etLYcY_y56JQMnTkz1k7K28hWfeM';

      // Array of API discovery doc URLs for APIs used by the quickstart
      var DISCOVERY_DOCS = ["https://www.googleapis.com/discovery/v1/apis/people/v1/rest"];

      // Authorization scopes required by the API; multiple scopes can be
      // included, separated by spaces.
      var SCOPES = "https://www.googleapis.com/auth/contacts";
      var contact_list = document.getElementById('contact-list');
      var phone_list = document.getElementById('phones');
      var contact_name = document.getElementById('person')
      var contact_after_me = document.getElementById('after_me');
      var connectionBtn = document.getElementById('connection-btn');
      var searchInput = document.getElementById('name-a49c');
      var modal = document.getElementById("myModal");
      var timer_div = document.getElementById('timer-div');
      var timer = document.getElementById('timer')
      /**
       *  On load, called to load the auth2 library and API client library.
       */
      function handleClientLoad() {
        gapi.load('client:auth2', initClient);
      }

      /**
       *  Initializes the API client library and sets up sign-in state
       *  listeners.
       */
      function initClient() {
        gapi.client.init({
          apiKey: API_KEY,
          clientId: CLIENT_ID,
          discoveryDocs: DISCOVERY_DOCS,
          scope: SCOPES
        }).then(function () {
          // Listen for sign-in state changes.
          gapi.auth2.getAuthInstance().isSignedIn.listen(updateSigninStatus);

          // Handle the initial sign-in state.
          updateSigninStatus(gapi.auth2.getAuthInstance().isSignedIn.get());
        }, function(error) {
          appendPre(JSON.stringify(error, null, 2));
        });
      }

      /**
       *  Called when the signed in status changes, to update the UI
       *  appropriately. After a sign-in, the API is called.
       */
      function updateSigninStatus(isSignedIn) {
        if (isSignedIn) {
          connectionBtn.onclick = handleSignoutClick;
          connectionBtn.innerHTML = 'Disconnect'
            document.getElementById('desc-connection').innerHTML = 'Disconnect Google Contacts'
          listConnectionNames();
        } else {
          connectionBtn.onclick = handleAuthClick;
          connectionBtn.innerHTML = 'Connect'
            document.getElementById('desc-connection').innerHTML = 'Connect to Google Contacts'
        }
      }

      /**
       *  Sign in the user upon button click.
       */
      function handleAuthClick(event) {
        gapi.auth2.getAuthInstance().signIn();
      }

      /**
       *  Sign out the user upon button click.
       */
      function handleSignoutClick(event) {
        gapi.auth2.getAuthInstance().signOut();
      }

      /**
       * Append a pre element to the body containing the given message
       * as its text node. Used to display the results of the API call.
       *
       * @param name
       * @param index
       */


      function appendPre(name, url, index) {
        contact_list.insertAdjacentHTML('beforeend',
            `<div id="contact-list-${index}" onclick="displayContactInfo(${index});" class="card2 u-container-style u-grey-5 u-list-item u-radius-5 u-repeater-item u-shape-round u-list-item-1">
                        <div class="u-container-layout u-similar-container u-container-layout-2">
                          <div style="background-image: url('${url}');" class="u-image u-image-circle u-image-1" alt="" data-image-width="1280" data-image-height="853"></div>
                          <h4 class="u-text u-text-default u-text-3">${name}</h4>
                        </div>
                      </div>`);
      }

      /**
       * Print the display name if available for 10 connections.
       */
      var people = [];
      function listConnectionNames() {
        gapi.client.people.people.connections.list({
           'resourceName': 'people/me',
            'sortOrder': 'FIRST_NAME_ASCENDING',
           'personFields': 'names,phoneNumbers,photos',
         }).then(function(response) {
           var connections = response.result.connections;
           if (connections.length > 0) {
               contact_after_me.innerHTML = `${connections.length} Contacts`;
             for (i = 0; i < connections.length; i++) {
               people[i] = connections[i];
               if (people[i].names && people[i].names.length > 0 && people[i].phoneNumbers && people[i].phoneNumbers.length > 0) {
                 appendPre(people[i].names[0].displayName, people[i].photos[0].url,  i)
               }
             }
           } else{
               contact_after_me.innerHTML = '0 Contacts';
           }
         });
      }

      function displayContactInfo(index){
          reset()
          timer.style.display = 'none';
          modal.style.display ='block';
          let person = people[index];
          contact_name.innerHTML = person.names[0].displayName;
          phone_list.innerHTML = '<div id="phone-after-me"></div>';
          let phone_after_me = document.getElementById('phone-after-me');
          for(i = 0; i < person.phoneNumbers.length; i++){
                phone_after_me.insertAdjacentHTML('afterend',
                `<a onclick="loading('${person.names[0].displayName}', '${person.phoneNumbers[i].value}');" style="padding: 10px 10px 10px 10px; color: black;" class="list-group-item">
                            ${person.phoneNumbers[i].value}
                </a>`);
          }
      }

      var close = document.getElementById('close')
      var btn = document.getElementById("myBtn");
      var span = document.getElementsByClassName("close")[0];

      close.onclick = function() {
          modal.style.display = "none";
      }

      function loading(name, phone){
          set()
          var timeleft = 1;
          var downloadTimer = setInterval(function(){
              if(timeleft >= 15){
                  reset()
                  timer.innerHTML = `${name} didn't respond to your call`;
                  clearInterval(downloadTimer);
              }
              create_post(phone, downloadTimer)
              timer.innerHTML = `Calling..., Wait for ${15 - timeleft} seconds`;
              timeleft += 1;
              }, 1000);
      }

      function onSearch(){
          let filter = searchInput.value.toUpperCase();
          let children = contact_list.children;
          let h4 = '';
          let txtValue = '';
          let count = 0;
          for(let i = 1; i < children.length; i++){
              let child = children[i];
              h4 = child.getElementsByTagName('h4')[0];
              txtValue = h4.textContent || h4.innerText;
              if (filter === '' || txtValue.toUpperCase().indexOf(filter) > -1) {
                  child.style.display = "";
                  count++;
              } else {
                  child.style.display = "none";
              }
          }
          contact_after_me.innerHTML = `${count} Contacts`;
      }

      function reset(){
          timer_div.style.marginTop = '0px'
          timer_div.style.display = 'none'
          timer.innerHTML = '';
      }

      function set(){
          timer_div.style.marginTop = '20px'
          timer.style.display = 'block';
          timer_div.style.display = 'block';
          timer.innerHTML = '';
      }
