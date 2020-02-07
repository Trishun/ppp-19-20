function add() {
    send("/api/add");
}

function check(checkbox) {
    send("/api/update?id="+checkbox.name+"&checked="+checkbox.checked);
}

function update(textInput) {
    send("/api/update?id="+textInput.name+"&value="+textInput.value);
}

function remove(button) {
    send("/api/remove/"+button.name);
}

function send(url) {
    $.ajax({
        url: url,
        success: function () {
            location.reload();
        }
    });
}

$('input').blur(function() {update(this)});