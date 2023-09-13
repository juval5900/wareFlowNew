(function () {
  "use strict";

  /*==================================================================
  [ Validate ]*/
  var name = document.getElementById("t1");
  var uname = document.getElementById("t2");
  var email = document.getElementById("t3");
  var passwd = document.getElementById("t5");
  var cpasswd = document.getElementById("t6");

  document.querySelector('.validate-form').addEventListener('submit', function (event) {
    var check = true;

    if (!validateName()) {
      showValidate(name);
      check = false;
    }

    if (!validateUname()) {
      showValidate(uname);
      check = false;
    }

    if (!validateEmail()) {
      showValidate(email);
      check = false;
    }
    if (!validatePwd()) {
      showValidate(passwd);
      check = false;
    }
    if (!validateCpwd()) {
      showValidate(cpasswd);
      check = false;
    }


    if (!check) {
      event.preventDefault(); // Prevent the form from submitting
    }
  });

  document.querySelectorAll('.validate-form .input100').forEach(function (element) {
    element.addEventListener('focus', function () {
      hideValidate(this);
    });
  });

  function validateName() {
    var letters = /^[A-Za-z ]*$/;
    // alert("Working")
    var fname = document.getElementById("t1").value;

    if ((!letters.test(fname) || fname.length <= 2) && fname.length > 0 || fname == "") {

      return false;
    } else {

      return true;
    }
  }

  function validateUname() {
    // alert("hello user")
    var letters = /^[A-Za-z ]*$/;
    var uname = document.getElementById("t2").value;
    if ((!letters.test(uname) || uname.length <= 2) && uname.length > 0 || uname == "") {

      return false;
    } else {

      return true;
    }
  }

  function validateEmail() {
    var email_exp = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;
    var email = document.getElementById("t3").value;
    if (!email_exp.test(email) || !(email.length > 0) || email == "") {
      return false;
    } else {
      return true;
    }
  }

  function validatePwd() {
    var pwd_exp = /^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-])/;
    var pwd = document.getElementById("t5").value;
    if (!pwd_exp.test(pwd) || (pwd.length <= 5) || (pwd.length > 12) || pwd == "") {
      return false;
    } else {
      return true;
    }
  }

  function validateCpwd() {
    var cpwd = document.getElementById("t6").value;
    var pwd = document.getElementById("t5").value;
    if (pwd !== cpwd || cpwd == "") {
      return false;
    } else {

      return true;
    }
  }

  function showValidate(input) {
    var thisAlert = input.parentNode;

    thisAlert.classList.add('alert-validate');
  }

  function hideValidate(input) {
    var thisAlert = input.parentNode;

    thisAlert.classList.remove('alert-validate');
  }



  $(document).ready(function() {
    const emailInput = $('#email');
    const usernameInput = $('#name');
    const emailError = $('#emailError');
    const usernameError = $('#nameError');
    
    emailInput.on('input', function() {
        const enteredEmail = $(this).val();
        $.get('/check_email/', { email: enteredEmail }, function(data) {
            if (enteredEmail && data.exists) {
                emailError.text('Email already taken');
            } else {
                validateField(emailInput, emailError, validateEmail);
            }
        });
    });
    
    usernameInput.on('input', function() {
        const enteredUsername = $(this).val();
        $.get('/check_username/', { username: enteredUsername }, function(data) {
            if (enteredUsername && data.exists) {
                usernameError.text('Username already taken');
            } else {
                validateField(nameInput, nameError, validateName);
            }
        });
    });
             });

document.addEventListener("DOMContentLoaded", function() {
  const usernameField = document.getElementById("username");
  const usernameError = document.getElementById("username-error");
  const registrationForm = document.querySelector("form[name='registration-form']");

  usernameField.addEventListener("blur", async function() {
      const username = usernameField.value;

      if (username) {
          const response = await fetch('/check-username-exists/?username=${username}');
          const data = await response.json();

          if (data.exists) {
              usernameError.textContent = "Username Already Exists";
              registrationForm.classList.add("has-error");
          } else {
              usernameError.textContent = "";
              registrationForm.classList.remove("has-error");
          }
      }
  });
});




})();
