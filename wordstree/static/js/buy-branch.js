$('#buyModal').on('show.bs.modal', function (event) {

  var button = $(event.relatedTarget); // Button that triggered the modal
  var branch_id = button.data('id');
  var branch_text = button.data('text');
  var branch_price = button.data('price');// Extract info from data-* attributes
  var modal = $(this);
  modal.find('#branch_name').text(branch_text);
  modal.find('#branch_price').text(branch_price);
  modal.find('.branch_id').val(branch_id);

})
