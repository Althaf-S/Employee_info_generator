function gotEmployees(data) {
    console.log(data);
    $("#userdetails")[0].innerHTML=`<h1> Details for ${data.firstname}  ${data.lastname}</h1>
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
`;



}

$(function() {
    $("a.userlink").click(function (ev) {
        $.get(ev.target.href, gotEmployees);
        ev.preventDefault();
        });
});
