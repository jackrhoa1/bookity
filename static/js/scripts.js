const submit_button = document.getElementById('new-name-submit');
const table = document.query

const bookTable = document.getElementById('book-table')

// testing connecting data

// end testing connecting data

function openTagEditBox(rowNum) {
    console.log("SUBMIT RN: " + rowNum)

    const actualRowIndex = parseInt(rowNum) + 1;
    const edit_img = document.getElementById('edit-tag-' + rowNum)
    const tag_data = document.getElementById('actual-tag-' + rowNum)
    // tag_data.hidden = true
    // edit_img.hidden = true
    const inlineInputBox = document.getElementById('tag-input-' + rowNum);
    inlineInputBox.hidden = !(inlineInputBox.hidden);
    const inlineSubmitButton = document.getElementById('new-tag-submit-' + rowNum);
    bookTable.rows[actualRowIndex]
    inlineSubmitButton.hidden = !(inlineSubmitButton.hidden);
    
    // inputText.hidden = false;
    // submit_button.hidden = false;
    // const actualRowIndex = parseInt(row_num) + 1;
    // book_table.rows[actualRowIndex].cells[0].textContent = input_text.value;
    // console.log(row_num);
}

function submit(rowNum) {
    console.log("SUBMIT RN: " + rowNum)
    const actualRowIndex = parseInt(rowNum) + 1;
    const inlineInputBox = document.getElementById('tag-input-' + rowNum);
    
    tag_data = bookTable.rows[actualRowIndex].cells[5]
    console.log(tag_data)
    tag_data = inlineInputBox.value;
    const isbn = bookTable.rows[actualRowIndex].cells[3].textContent
    const edit_img = document.getElementById('edit-tag-' + rowNum)
    edit_img.hidden = true
    
    change_data_table(inlineInputBox.value, isbn);
    // inlineInputBox.value is the text we want to send

}

function change_data_table(newTag, id) {
    const newData = {
        id: id,
        tag: newTag
    };
    fetch(`${window.origin}/my-library/modify-tag`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(newData),
        cache: "no-cache",
        headers: new Headers({
          "Content-Type": "application/json",
        }),
      }).then(function (response) {
        if (response.status != 200) {
          console.log(`Response status was ${response.status}`);
          return;
        }
        response.json().then(function (data) {
          console.log(data);
        });
      });
}

function submit_entry() {
    const name = document.getElementById("name");
    const message = document.getElementById("message");

    const entry = {
      name: name.value,
      message: message.value,
    };
    fetch(`${window.origin}/guestbook/create-entry`, {
      method: "POST",
      credentials: "include",
      body: JSON.stringify(entry),
      cache: "no-cache",
      headers: new Headers({
        "Content-Type": "application/json",
      }),
    }).then(function (response) {
      if (response.status != 200) {
        console.log(`Response status was ${response.status}`);
        return;
      }
      response.json().then(function (data) {
        console.log(data);
      });
    });
  }