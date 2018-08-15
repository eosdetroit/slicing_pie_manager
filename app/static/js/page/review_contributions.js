$(function () {
   $(".approve-contribution").on('click', function () {
       var $row = $(this).parents("tr");
       var contribution_id = $row.children(".contribution_id").text();
       var url = "/contributions/review/approve/" + contribution_id;
       console.log(url);

       $.ajax({
           url: url,
           type: "POST",
           data: { csrf_token: csrf_token },
           success: function (result) {
               $row.remove();
           }
       })
   });
   $(".deny-contribution").on('click', function () {
       var $row = $(this).parents("tr");
       var contribution_id = $row.children(".contribution_id").text();
       var url = "/contributions/review/deny/" + contribution_id;
       console.log(url);

       $.ajax({
       	   url: url,
       	   type: "POST",
       	   data: { csrf_token: csrf_token },
       	   success: function (result) {
               $row.remove();
       	   }
       })
   });
});