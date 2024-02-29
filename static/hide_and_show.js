function hide() {
  const x = document.getElementById("comments_section");
  const btn = document.getElementById("show_btn");
  if (x.style.display === "block") {
    x.style.display = "none";
    btn.style.display="block";

  } else {

    x.style.display = "block";
    btn.style.display="none";
  }
}