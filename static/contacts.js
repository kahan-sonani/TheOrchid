
      // Client ID and API key from the Developer Console
      var CLIENT_ID = '456816466000-fllno6mknd0nq7fivp486gkd7f35g00f';
      var API_KEY = 'AIzaSyCMTx5etLYcY_y56JQMnTkz1k7K28hWfeM';

      // Array of API discovery doc URLs for APIs used by the quickstart
      var DISCOVERY_DOCS = ["https://www.googleapis.com/discovery/v1/apis/people/v1/rest"];

      // Authorization scopes required by the API; multiple scopes can be
      // included, separated by spaces.
      var SCOPES = "https://www.googleapis.com/auth/contacts";
      var list = document.getElementById('phone-after-me');
      var contactList = document.getElementById('after_me');
      var connectionBtn = document.getElementById('connection-btn');

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
            document.getElementById('desc-connection').innerHTML = '   Connect with Google Contacts'
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
       * @param phone
       */


      function appendPre(name, index) {
        contactList.insertAdjacentHTML('afterend',
            `<div id="myBtn" onclick="displayContactInfo(${index});" class="card2 u-container-style u-grey-5 u-list-item u-radius-5 u-repeater-item u-shape-round u-list-item-1">
                        <div class="u-container-layout u-similar-container u-container-layout-2">
                          <div class="u-image u-image-circle u-image-1" alt="" data-image-width="1280" data-image-height="853"></div>
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
           'personFields': 'names,phoneNumbers',
         }).then(function(response) {
           var connections = response.result.connections;
           if (connections.length > 0) {
             for (i = 0; i < connections.length; i++) {
               people[i] = connections[i];
               if (people[i].names && people[i].names.length > 0 && people[i].phoneNumbers && people[i].phoneNumbers.length > 0) {
                 appendPre(people[i].names[0].displayName, i)
               }
             }
           }
         });
      }

      var modal = document.getElementById("myModal");
      function displayContactInfo(index){
          modal.style.display ='block';
          let person = people[index];
          console.log(person)
          document.getElementById('person').innerHTML = person.names[0].displayName;
          list.innerHTML = '';
          for(i = 0; i < person.phoneNumbers.length; i++){
                list.insertAdjacentHTML('afterend',
                `<a href="#" style="padding: 10px 10px 10px 10px" class="list-group-item">
                            ${person.phoneNumbers[i].value}
                </a>`);
          }
      }
        var close = document.getElementById('close')

        var btn = document.getElementById("myBtn");

        // Get the <span> element that closes the modal
        var span = document.getElementsByClassName("close")[0];

        // When the user clicks on the button, open the modal

        // When the user clicks anywhere outside of the modal, close it
        close.onclick = function() {
            modal.style.display = "none";
        }
