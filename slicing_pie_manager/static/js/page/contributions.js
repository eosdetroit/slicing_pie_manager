$(function () {
   $(document).on('click', ".edit-contribution", function () {
       var $row = $(this).parents("tr");
       console.log("pri")
       var contribution_id = $row.children(".contribution_id").text();
       var task = $row.children(".task").text();
       var work_rate_id = $row.children(".work_rate").data("value");
       var role_id = $row.children(".role").data("value");
       var hours_spent = $row.children(".hours_spent").text();
       var cash_spent = $row.children(".cash_spent").text();
       var contribution_date = $row.children(".contribution_date").text();
       var $editForm = $("#edit-modal").find("form");
       $editForm.attr("action", "/contributions/" + contribution_id);
       $editForm.find("#edit_work_rate").val(work_rate_id);
       $editForm.find("#edit_role").val(role_id);
       $editForm.find("#edit_task").val(task);
       $editForm.find("#edit_hours_spent").val(hours_spent);
       $editForm.find("#edit_cash_spent").val(cash_spent);
       $editForm.find("#edit_contribution_date").val(contribution_date);
   });

   $(document).on('click', ".delete-contribution", function () {
       var $row = $(this).parents("tr");
       var contribution_id = $row.children(".contribution_id").text();
       var url = "/contributions/delete/" + contribution_id;
       console.log(url);

       var csrf_token = $("#csrf_token").val();
       $.ajax({
       	   url: url,
       	   type: "POST",
       	   data: { csrf_token: csrf_token },
       	   success: function (result) {
               $row.remove();
       	   }
       })
   });
   $(".flatpickr").datetimepicker({
	   inline: true,
	   sideBySide: true,
	   format: "YYYY-MM-DD HH:mm:ss"
   });
});