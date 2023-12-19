function gotEmployees(data) {
    console.log(data);
    $("#userdetails")[0].innerHTML=`<div id="successMessage"></div>
   <h1> Details for ${data.firstname}  ${data.lastname}</h1>
    <h2> ${data.title} </h2>
    <table>
      <tr>
        <th> First name </th>
        <td> ${data.firstname}</td>
      </tr>
      <tr>
        <th> Last name </th>
        <td> ${data.lastname}</td>
      </tr>
      <tr>
        <th> Email </th>
        <td> ${data.email}</td>
      </tr>
      <tr>
        <th> Phone </th>
        <td> ${data.phone}</td>
      </tr>
      <tr>
        <th> Number of leaves taken </th>
          <td> ${data.leaves}</td>
      </tr>
      <tr>
        <th>Maximum number of leaves</th>
          <td> ${data.max_leaves}</td>
      </tr>
    </table>
        <h1> Enter leave data for user </h1>
<form action = /leave/${data.employee_id} method="post" id="leaveForm">
    <label for="date">Date:</label>
    <input type="date" name="date" required>
    <br>
    <label for="reason">Reason:</label>
    <textarea id="reason" name="reason" rows="4" cols="10" required></textarea>
    <br>
    <input type="submit" value="Submit">
</form>
`;

}



$(function() {
    $("a.userlink").click(function (ev) {
        $.get(ev.target.href, gotEmployees);
        ev.preventDefault();
    });
    $("#userdetails").on("submit", "#leaveForm", function(event) {
        event.preventDefault();
        
        var formData = $(this).serialize();
        
        $.ajax({
            url: $(this).attr("action"),
            type: "POST",
            data: formData,
             success: function(response) {
            alert("Form submitted successfully");
            window.location.href = "/employees";
    },
            error: function(error) {
                alert("Form not submitted because same data present in database");
            }
        });
    });
});







