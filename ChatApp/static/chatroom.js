function get(selector, root = document) {
    return root.querySelector(selector);
}
const msgerForm = get(".msger-inputarea");
const msgerInput = get(".msger-input");
const msgerChat = get(".msger-chat");

const ROOT_URL = "http://localhost:5000"

const TIME_UPDATECHAT = 1000 //1sec
const TIME_MINEBLOCK = 5000 //5sec

var messages = []
var USERNAME = null

// -----------------------------------------------

// Function to submit message
msgerForm.addEventListener("submit", event => {
    event.preventDefault();

    const msgText = msgerInput.value;
    if (!msgText) return;
    document.getElementById("send_msg_field").value = ""; 
    // TODO: compute h and send {sender, msg, h} to /add_data and b is returned in response
    // use that to calculate s and send {s} to /add_data again
    let h = 0
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
    $.ajax(settings).done(function (response) {
        b = response['b']
    });

    let s = 2
    // TODO: compute s
    settings = {
        "url": api_url,
        "method": "POST",
        "headers": {
          "Content-Type": "application/json"
        },
        "data": JSON.stringify({"s":s}),
      };
      
      $.ajax(settings).done(function (response) {
        updateChatBox();
      });
});


// -----------------------------------
// Helper Functions To Update Chatroom messages

function appendMessage(name, text, time, side) {
const msgHTML = `
    <div class="msg ${side}-msg">
    <div class="msg-bubble">
        <div class="msg-info">
        <div class="msg-info-name">${name}</div>
        <div class="msg-info-time">${time}</div>
        </div>

        <div class="msg-text">${text}</div>
    </div>
    </div>
    `;
    msgerChat.insertAdjacentHTML("beforeend", msgHTML);
    msgerChat.scrollTop += 500;
}

function addResponseToMessages(response) {
    mined_data = response['chain'];
    unmined_data = response['unmined_msgs'];
    if(messages.length == (mined_data.length+unmined_data.length-1)) {
        console.log("Same length")
        return;
    }
    messages = []
    for(let i = 1; i < mined_data.length; ++i) {
        data = mined_data[i]['data'];
        for(let j = 0; j < data.length; ++j) {
            messages.push(data[j]);
        }
    }
    for(let i = 0; i < unmined_data.length; ++i) {
        messages.push(unmined_data[i]);
    }
}

function updateChatBox() {
    console.log(USERNAME)
    api_url = ROOT_URL + "/get_chain"
    let settings = {
        "url": api_url,
        "method": "GET"
    };
    $.ajax(settings).done(function (response) {
        let prev_msgs_len = messages.length;
        addResponseToMessages(response);
        if(prev_msgs_len === messages.length) {
            console.log("Upto-date");
            return;
        }
        console.log(messages)
        for(let i = prev_msgs_len; i < messages.length; ++i) {
            name = messages[i]['sender']
            console.log(name)
            text = messages[i]['msg']
            time = messages[i]['time']
            if(name == USERNAME)
                side = "right"
            else
                side = "left"
            appendMessage(name, text, time, side)
        }
    });
}
$(document).ready(function() {
    USERNAME = document.getElementById("logout").value
    updateChatBox();
});

// setInterval(function() {updateChatBox();}, TIME_UPDATECHAT);

// -------------------------------------------------------

// Helper functions to mine blocks

function mineBlock() {
    let api_url = ROOT_URL + "/mine_block"
    let settings = {
        "url": api_url,
        "method": "GET"
    };

    $.ajax(settings).done(function (response) {
        console.log(response);
    });
}

// setInterval(function() {mineBlock();}, TIME_MINEBLOCK);

// Helper function to logout an user

function logout1() {
    console.log("Calling /logout in the server to decrease # of logged_in users")
    // mineBlock()
    let api_url = ROOT_URL + "/logout"
    let settings = {
        "url": api_url,
        "method": "GET"
    };

    $.ajax(settings).done(function (response) {
        console.log(response);
    });
}

function logout2() {
    console.log("Redirecting")
    window.location.href = ROOT_URL;
}
function logout() {
    logout1()
    setTimeout(function(){
        logout2()
    }, 2000)
}