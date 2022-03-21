function myFunction() {
  var x = document.getElementById("password-b604");
  if (x.type === "password") {
    x.type = "text";
  } else {
    x.type = "password";
  }
}