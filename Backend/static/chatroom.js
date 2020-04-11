// Utils
function get(selector, root = document) {
    return root.querySelector(selector);
}
  
function formatDate(date) {
    const h = "0" + date.getHours();
    const m = "0" + date.getMinutes();

    return `${h.slice(-2)}:${m.slice(-2)}`;
}
  
const msgerForm = get(".msger-inputarea");
const msgerInput = get(".msger-input");
const msgerChat = get(".msger-chat");

const ROOT_URL = "http://localhost:5000"


// TODO: This will be array of jsons. This list will be updated with API call
let messages = [
    {
        "sender": "rohit",
        "msg": "Test1",
        "timestamp": "2020-04-11 18:52:26.727324"
    },
    {
        "sender": "charan",
        "msg": "Test2",
        "timestamp": "2020-04-11 18:54:26.727324"
    }       
]
msgerForm.addEventListener("submit", event => {
    const USERNAME = document.getElementById("logout").value
    event.preventDefault();

    const msgText = msgerInput.value;
    if (!msgText) return;

    // TODO: compute h and send {sender, msg, h} to /add_data and b is returned in response
    // use that to calculate s and send {s} to /add_data again
    let h = 1
    api_url = ROOT_URL + "/add_data"
    let settings = {
        "url": api_url,
        "method": "POST",
        "headers": {
          "Content-Type": "application/json"
        },
        "data": JSON.stringify({"h":h,"msg":msgText,"sender":USERNAME}),
    };
    let b = 0
    let b_changed = false
    $.ajax(settings).done(function (response) {
        b = response['b'];
        b_changed = true
    });
    if(b_changed == false) console.log("Error in getting b as response from /add_data")

    let s = 0
    // TODO: compute s
    let settings = {
        "url": api_url,
        "method": "POST",
        "headers": {
          "Content-Type": "application/json"
        },
        "data": JSON.stringify({"s":s}),
      };
      
      $.ajax(settings).done(function (response) {
        console.log(response);
      });
    //
    
    messages.append(
        {
            "sender": USERNAME,
            "msg": msgText,
            "timestamp": "2020-04-11 18:52:26.727324"
        }
    );
    // updateChatBox();
    //This functions appends the message to our chat. Instead of doing this maybe update all messages?
    // appendMessage(USERNAME, "right", msgText);  
    // msgerInput.value = "";                      

});


function updateChatBox() {
    
    //TODO:
}

function appendMessage(name, side, text) {
const msgHTML = `
    <div class="msg ${side}-msg">
    <div class="msg-bubble">
        <div class="msg-info">
        <div class="msg-info-name">${name}</div>
        <div class="msg-info-time">${formatDate(new Date())}</div>
        </div>

        <div class="msg-text">${text}</div>
    </div>
    </div>
`;

msgerChat.insertAdjacentHTML("beforeend", msgHTML);
msgerChat.scrollTop += 500;
}
