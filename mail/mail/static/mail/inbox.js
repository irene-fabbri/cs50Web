document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM fully loaded and parsed');
  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => {
    console.log('Inbox button clicked');
    load_mailbox('inbox');
  });
  document.querySelector('#sent').addEventListener('click', () => {
    console.log('Sent button clicked');
    load_mailbox('sent');
  });
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  // Listen for an email submission
  document.querySelector('#compose-form').addEventListener('submit', send_email);
  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#single-email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

}

function answer_email(email) {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#single-email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  if( !email['subject'].toLowerCase().startsWith('re')) {
    document.querySelector('#compose-subject').value = `Re: ${email['subject']}`;
  }
  document.querySelector('#compose-body').value = `On ${email['timestamp']}, ${email['sender']} wrote: ${email['body']}`;

}

function send_email(event) {
  event.preventDefault();

  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: document.querySelector('#compose-recipients').value,
        subject: document.querySelector('#compose-subject').value,
        body: document.querySelector('#compose-body').value
    })
  })
  .then(response => response.json())
  .then(result => {
      // Print result
      console.log(result);
      load_mailbox('sent');
  });

}

function load_mailbox(mailbox) {

  let emails_view = document.querySelector('#emails-view')

  // Show the mailbox and hide other views
  emails_view.style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#single-email-view').style.display = 'none';

  // Show the mailbox name
  emails_view.innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
      // Print emails
      console.log(emails);
      emails.forEach((email) => {
        // create the email box
        let box = document.createElement('div')
        if (email['read']){
          box.setAttribute('class', 'mail-box read')
        }
        else {
          box.setAttribute('class', 'mail-box unread')
        }
        box.innerHTML = `<b>${email['sender']}:</b> ${email['subject']} <span class="timestamp">${email['timestamp']}</span>`
        // add event listener to read when clicked
        box.addEventListener('click', () => read_email(email['id']));
        // attach it to the email-view
        emails_view.append(box)
      });

  });
}

function read_email(email_id) {

  let user = document.body.getAttribute('data-user-email');

  let single_email_view = document.querySelector('#single-email-view')
  single_email_view.innerHTML=''

  // Show the single mail view and hide other views
  single_email_view.style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#emails-view').style.display = 'none';

  // mark as read
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
        read: true
    })
  })
  .then(response => {
    if (response.ok) {
      // Update the local email object here
      console.log("Email marked as read");
      return fetch(`/emails/${email_id}`);
    } else {
      console.error("Failed to update email status");
    }
  })
  .then(response => response.json())
  .then(email => {
      // Print email
      console.log(email);
      // From
      let from = document.createElement('div')
      from.innerHTML = `<b>From: </b>${email['sender']}`
      // To
      let to = document.createElement('div')
      to.innerHTML = `<b>To: </b>${email['recipients']}`
      // Subject
      let subject = document.createElement('div')
      subject.innerHTML = `<b>Subject: </b>${email['subject']}`
      // Timestamp
      let timestamp = document.createElement('div')
      timestamp.innerHTML = `<b>Timestamp: </b>${email['timestamp']}`

      let body = document.createElement('div')
      body.setAttribute('class','mail-body')
      body.innerHTML = `${email['body']}`
      let button_box = document.createElement('div')

      // toggle read/unread button
      let toggle_read = document.createElement('button')
      toggle_read.innerHTML = email.read ? 'Mark as Unread' : 'Mark as Read';
      toggle_read.setAttribute('class','btn btn-sm btn-primary me-2')
      toggle_read.addEventListener('click', () => {
        let new_read_status = !email.read;
        fetch(`/emails/${email_id}`, {
          method: 'PUT',
          body: JSON.stringify({
              read: new_read_status
          })
        })
        .then(() => {
          email.read = new_read_status; // Update the local email object
          toggle_read.innerHTML = new_read_status ? 'Mark as Unread' : 'Mark as Read';
          console.log(`Email read status updated to: ${new_read_status}`);
        });
      });
      // reply button
      let reply_button = document.createElement('button');
      reply_button.setAttribute('class','btn btn-sm btn-primary me-2');
      reply_button.innerHTML = 'Reply';
      reply_button.addEventListener('click', () => answer_email(email));

      button_box.append(toggle_read)
      button_box.append(reply_button)


      single_email_view.append(from)
      single_email_view.append(to)
      single_email_view.append(timestamp)
      single_email_view.append(body)


      // toggle archive/unarchive button if the user is not the sender
      if (email.sender !== user) {
        let toggle_archived = document.createElement('button')
        toggle_archived.innerHTML = email.archived ? 'Unarchive Email' : 'Archive Email';
        toggle_archived.setAttribute('class','btn btn-sm btn-primary me-2')
        toggle_archived.addEventListener('click', () => {
          let new_archived_status = !email.archived;
          fetch(`/emails/${email_id}`, {
            method: 'PUT',
            body: JSON.stringify({
                archived: new_archived_status
            })
          })
          .then(() => {
            email.archived = new_archived_status; // Update the local email object
            toggle_archived.innerHTML = email.archived ? 'Unarchive Email' : 'Archive Email';
            console.log(`Email archived status updated to: ${new_archived_status}`);
            load_mailbox('inbox');
          });
        });
        button_box.append(toggle_archived)
      }
      single_email_view.append(button_box)

  });

}
