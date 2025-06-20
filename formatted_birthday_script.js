function sendBirthdayEmails() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Sheet1"); // Change name if needed
  var data = sheet.getDataRange().getValues();
  var today = new Date();
  var todayStr = Utilities.formatDate(today, Session.getScriptTimeZone(), "MM/dd");
  var isWeekend = today.getDay() === 6 || today.getDay() === 0; // Saturday or Sunday
  
  // Skip processing if today is a weekend
  if (isWeekend) {
    return; // Don't send any emails on weekends
  }
  
  for (var i = 1; i < data.length; i++) {
    var name = data[i][0];
    var email = data[i][1];
    var birthday = new Date(data[i][2]);
    var lastSent = data[i][3];
    var department = data[i][4]; // Fetching the department dynamically
    var ccEmail = data[i][5]; // Fetch LT email for CC
    var birthdayStr = Utilities.formatDate(birthday, Session.getScriptTimeZone(), "MM/dd");
    var birthdayDay = birthday.getDay(); // Day of the week (0 = Sunday, 6 = Saturday)
    var birthdayDayName = getDayName(birthdayDay);
    
    // Weekend birthday logic - send on Friday before the weekend birthday
    if ((birthdayDay === 0 || birthdayDay === 6) &&
        today.getDay() === 5 && // Today is Friday
        isWeekendBirthdayComingUp(birthdayStr)) {
      if (!lastSent || new Date(lastSent).getFullYear() < today.getFullYear()) {
        var weekendMessage;
        if (birthdayDay === 6) { // Saturday
          weekendMessage = `Happy Birthday Tomorrow ${name}!`;
        } else { // Sunday
          weekendMessage = `Happy birthday on ${birthdayDayName} ${name}!`;
        }
        sendCustomEmail(name, email, department, ccEmail, weekendMessage);
        sheet.getRange(i + 1, 4).setValue(today); // Update last sent date
      }
    }
    // Normal weekday birthday logic
    else if (todayStr === birthdayStr && 
             (!lastSent || new Date(lastSent).getFullYear() < today.getFullYear())) {
      sendCustomEmail(name, email, department, ccEmail, `Happy birthday ${name}!`);
      sheet.getRange(i + 1, 4).setValue(today);
    }
  }
}

function sendCustomEmail(name, email, department, ccEmail, greeting) {
  var subject = `Happy Birthday, ${name}!`;
  var body = `
    <p>${greeting}</p>
    <p>Wishing you a great day filled with joy, laughter, and everything you love.</p>
    <p>Your contributions to the ${department} team are much appreciated.</p>
    <p>Thank you for your continued push.</p>
    <img src="https://drive.google.com/uc?export=view&id=1S9djCu286ljS75x2SMST3hDhFCS1tPJa" width="400">
    <p>Here's to another amazing year ahead.</p>

    <p>Tuchape kazi, tujifunze, pamoja!</p>
    <p>/Tomas</p>
  `;
  
  MailApp.sendEmail({
    to: email,
    cc: ccEmail, // Adding the CC field
    subject: subject,
    htmlBody: body
  });
}

// Helper function to check if a weekend birthday is coming up
function isWeekendBirthdayComingUp(birthdayStr) {
  var today = new Date();
  // Calculate Saturday and Sunday dates
  var saturdayDate = new Date(today);
  saturdayDate.setDate(today.getDate() + 1); // Tomorrow is Saturday if today is Friday
  var saturdayStr = Utilities.formatDate(saturdayDate, Session.getScriptTimeZone(), "MM/dd");
  
  var sundayDate = new Date(today);
  sundayDate.setDate(today.getDate() + 2); // Day after tomorrow is Sunday if today is Friday
  var sundayStr = Utilities.formatDate(sundayDate, Session.getScriptTimeZone(), "MM/dd");
  
  // Check if birthday is on the upcoming Saturday or Sunday
  return birthdayStr === saturdayStr || birthdayStr === sundayStr;
}

function getDayName(dayIndex) {
  var days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  return days[dayIndex];
}
