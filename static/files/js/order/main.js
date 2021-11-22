

$(document).ready(function () {
 /* $("#content-slider").lightSlider({

          item:2,
          loop:true,
          slideMove:1,
          speed:600,
         
  });*/
  console.log("moment date is "+ moment().format('MM/DD/YYYY'))
  $('#calendar').datepicker({
    language: "en",
    startDate:moment().format('MM/DD/YYYY')
    
  });
  
  $('#calendar').on('changeDate', function() {
    $('#date_hidden').val(
        $('#calendar').datepicker('getFormattedDate')
    );
   // console.log("moment is")
    console.log($('#date_hidden').val()) 
    var date=$('#date_hidden').val()
    var day=date.split('/')[1]
    var month=date.split('/')[0]
    var year=date.split('/')[2]
    var newdate=day+'-'+month+'-'+year
    app.selected_date=newdate
    if(!app.selected_slots[app.selected_date])
    {
    app.selected_slots[app.selected_date]=[]
    }
    //console.log($('#date_hidden').val().replace(/\//g, '-'))
    app.setDate($('#date_hidden').val())
    this.selected_cleaning_date=moment(date,'MM/DD/YYYY').format('DD-MM-YYYY')
    app.getSlotes(moment(date,'MM/DD/YYYY').format('DD-MM-YYYY'))
   
    app.getVisitSlotes(moment(date,'MM/DD/YYYY').format('DD-MM-YYYY'))
});

  $(".owl-carousel").owlCarousel({
    items: 2,
    nav: true,
    margin: 10,
    navText: [
      `<i class='fa fa-chevron-left service-control' @click='prevService()'></i>`,
      `<i class='fa fa-chevron-right service-control'></i>`,
    ],
  });
   app.paymentType = $( "#id_payment" ).val()
  app.amount = $("#id_amount").text()

});



function limit(element)
{
    var max_chars = 300;

    if(element.value.length > max_chars) {
        element.value = element.value.substr(0, max_chars);
    }
}
function proceedImage(order){
 
 
}
function addImage(order){
  var eval_id=$(order).data('eval_id')
  $('#upload-image-tigger').click()
  app.image_eval_id=eval_id

}
function myFunction(book_id) {
  document.getElementById("visti-section"+book_id+"").classList.toggle("not-show");
  document.getElementById("myDropdown"+book_id+"").classList.toggle("show");
}
function onClick(element) {
  document.getElementById("img01").src = element.src;
  document.getElementById("modal01").style.display = "block";
}
function onClose() {
  
  document.getElementById("modal01").style.display = "none";
}
/*function editSection(section){
  console.log("i m here")
  var sectiondata=$(section).data()
  console.log("section is "+JSON.stringify(sectiondata))
  app.sectionData=sectiondata
  $('#edit-dialog-tigger').click()
  app.editSectionData.section_cost=sectiondata.section_cost
  app.editSectionData.section_name=sectiondata.section_name
  
}*/
function editCustmerNote(currentData){
  
  $('#customer_note-tigger').click()
  app.customer_note=$(currentData).data('current_note')
  
 
}
function editSection(service){
  
  
  var index=$(service).data('index')
  var sid=$(service).data('section_id')
  var eval_book_id=$(service).data('eval_book_id')
  app.action_type="Edit"

  app.service_type=$(service).data('service')
  app.getProductivity()
  console.log("index is"+index)
 // var sectiondata=$(section).data()
 app.getSection(eval_book_id)
 app.editSectionData.section_id=sid
 //app.editSectionData.addons=app.sections[index-1].addonsections
 app.kitchen_addons=app.sections[index-1].addonsections
 if(app.service_type=='General Cleaning' || app.service_type=='Deep Cleaning' || app.service_type=='Hourly Cleaning' ){
   for(var i=0;i<app.kitchen_addons.length;i++){
    app.kitchen_addons[i].other_details=JSON.parse( app.kitchen_addons[i].other_details)
    app.kitchen_addons[i].other_details.size=app.findKitchenSize(app.kitchen_addons[i].other_details.size,app.kitchen_addons[i].other_details.is_cabinet,app.kitchen_addons[i].other_details.type)
   }
 }
 
if(app.service_type=='Kitchen Cleaning'){
  app.editSectionData.new_kitchen=app.sections[index-1].new_kitchen
  app.editSectionData.oil_residue=app.sections[index-1].oil_residue
  app.editSectionData.is_cabinet=app.sections[index-1].is_cabinet
  
    app.getAddons()
  
  
}
if(app.service_type=='Kitchen Appliances'){
  app.getAddons()
}
if(app.service_type=='Facade Cleaning'){
  app.editSectionData.is_highprice_facade=app.sections[index-1].is_highprice_facade
  
}
if(app.service_type=='Window Cleaning'){
  app.editSectionData.is_highprice_window=app.sections[index-1].is_highprice_window
  
}
 app.editSectionData.keynotes=app.sections[index-1].keynotesections
  console.log("section is "+JSON.stringify(app.sections[index-1]))
  app.sectionData=app.sections[index-1]
  if(app.sections[index-1].size){
  app.editSectionData.size=app.sections[index-1].size
  app.editSectionData.size['combined_size']=app.sections[index-1].size.name+' ('+app.sections[index-1].size.min_size+' sq.m - '+app.sections[index-1].size.max_size+' sq.m )'
  }
  if(app.sections[index-1].upholstery_type){
    app.editSectionData.upholstery_type=app.sections[index-1].upholstery_type
  }
  app.getOtherKeynotes()
      app.getTheKitchens()
     
      app.recalcKeynoteCost()
  $('#edit-dialog-tigger').click()
  app.editSectionData.section_cost=app.sectionData.section_cost
  app.editSectionData.section_net_cost=app.sectionData.section_net_cost
  app.editSectionData.sectiononly_cost=app.sectionData.sectiononly_cost
  app.editSectionData.sectiononly_net_cost=app.sectionData.sectiononly_net_cost
  app.editSectionData.section_name=app.sectionData.section_name
  app.removeInitialKitchenCost()
  if(app.sectionData.wall_type!="" && app.sectionData.wall_type!=null)
  {
    app.editSectionData.wall_type=app.sectionData.wall_type.split(',')
  }
  if(app.sectionData.floor_type!="" && app.sectionData.floor_type!=null)
  {
    app.editSectionData.floor_type=app.sectionData.floor_type.split(',')
  }
  if(app.sectionData.ceiling_type!="" && app.sectionData.ceiling_type!=null)
  {
    app.editSectionData.ceiling_type=app.sectionData.ceiling_type.split(',')
  }
  if(app.sectionData.material!="" && app.sectionData.material!=null )
  {
    app.editSectionData.material=app.sectionData.material.split(',')
  }
  if(app.sectionData.age!="" && app.sectionData.age!=null )
  {
    app.editSectionData.age=app.sectionData.age.split(',')
  }
  if(app.sectionData.colour!="" && app.sectionData.colour!=null )
  {
    app.editSectionData.colour=app.sectionData.colour.split(',')
  }
  if(app.sectionData.age!="" && app.sectionData.age!=null )
  {
    app.editSectionData.age=app.sectionData.age.split(',')
  }
  if(app.sectionData.cause_of_stain!="" && app.sectionData.cause_of_stain!=null )
  {
    app.editSectionData.cause_of_stain=app.sectionData.cause_of_stain.split(',')
  }
  if(app.sectionData.age_of_stain!="" && app.sectionData.age_of_stain!=null )
  {
    app.editSectionData.age_of_stain=app.sectionData.age_of_stain
  }
  
  
  
  
  //app.findSize()
  
}

function editService(service){
  app.service_type=$(service).data('service')
  app.edit=true
  app.getProductivity()
  
}
function openPaymentEdit(payment){
 var paymentDetails=$(payment).data()
 app.paymentData.payment_method=paymentDetails.payment_method
 app.paymentData.total_amount=paymentDetails.total_amount
 app.paymentData.final_amount=paymentDetails.final_amount
 app.total_amount=paymentDetails.total_amount
 app.paymentData.discount=paymentDetails.discount
 app.paymentData.additional_charge=paymentDetails.additional_charge
 app.paymentData.amount_before_cleaning=paymentDetails.amount_before_cleaning
 app.paymentData.amount_after_cleaning=paymentDetails.amount_after_cleaning
 app.cancelledAmount=paymentDetails.cancelled_amount
 app.openPayment()
}
function openSubmit(payment){
  var paymentDetails=$(payment).data()
  app.paymentData.payment_method='PREPAID'
  app.paymentData.total_amount=paymentDetails.total_amount
  app.paymentData.final_amount=paymentDetails.final_amount
  app.paymentData.additional_charge=paymentDetails.additional_charge
  app.total_amount=paymentDetails.total_amount
  app.paymentData.discount=paymentDetails.discount
  app.paymentData.amount_before_cleaning=paymentDetails.amount_before_cleaning
  app.paymentData.amount_after_cleaning=paymentDetails.amount_after_cleaning
  
 }

function openCleaningDate(service){
  app.cleaning_action='add_cleaning'
  $('#cleaning-date-tigger').click()
  var data=$(service).data()
  app.no_of_cleaners=data.no_of_cleaners
  console.log("cleaners:"+data.no_of_cleaners)
  app.selected_no_of_cleaners=data.no_of_cleaners
  app.service_type=data.service
  app.cleaning_hours=parseInt(data.cleaning_hours)
  app.no_of_slots=Math.ceil(data.cleaning_hours/2)
  app.evaluation_book_id=data.evaluation_book_id
  
  app.getSlotes(moment().format('DD-MM-YYYY'))
  $("#calendar").datepicker("update", (moment().format('MM/DD/YYYY')));
}
function editCleaningDate(service){
  app.cleaning_action='edit_cleaning'
  $('#cleaning-date-tigger').click()
  var data=$(service).data()
  app.no_of_cleaners=data.no_of_cleaners
  app.selected_no_of_cleaners=data.no_of_cleaners
  app.service_type=data.service
  app.cleaning_hours=parseInt(data.cleaning_hours)
  app.no_of_slots=Math.ceil(data.cleaning_hours/2)
  app.evaluation_book_id=data.evaluation_book_id
  app.schedule_id=data.id
  
  app.cleaning_start_date=data.cleaning_start_date
  app.selected_cleaning_date=data.cleaning_start_date
  app.selected_date=data.cleaning_start_date
  app.selected_slots[app.selected_date]=[]
  app.getSlotes(app.cleaning_start_date)
  $('#date_hidden').val((moment(app.cleaning_start_date,'DD-MM-YYYY').format('MM/DD/YYYY')))
  $("#calendar").datepicker("update", moment(app.cleaning_start_date,'DD-MM-YYYY').format('MM/DD/YYYY'));
  app.setDate(moment(app.cleaning_start_date,'DD-MM-YYYY').format('MM/DD/YYYY'))
  
}
function deleteCleaningDate(service){
  app.cleaning_action='cancell_cleaning'
  app.reduction_status=false
  console.log("inside del cleaning")
  $('#cleaning-delete-tigger').click()
  var data=$(service).data()
  app.no_of_cleaners=data.no_of_cleaners
  app.cleaning_policy='ONE TIME SERVICE'
  app.selected_no_of_cleaners=data.no_of_cleaners
  app.service_type=data.service
  app.cleaning_hours=parseInt(data.cleaning_hours)
  app.no_of_slots=Math.ceil(data.cleaning_hours/2)
  app.evaluation_book_id=data.evaluation_book_id
  app.schedule_id=data.id
  
  app.cleaning_start_date=data.cleaning_start_date
  app.selected_cleaning_date=data.cleaning_start_date
 
}
function cancelCleaningDate(service){
 
  app.cleaning_action='cancell_cleaning'
  app.reduction_status=false
  $('#cleaning-cancel-tigger').click()
  var data=$(service).data()
  
  app.no_of_cleaners=data.no_of_cleaners
  app.cleaning_policy='SUBSCRIPTION'
  app.selected_no_of_cleaners=data.no_of_cleaners
  app.service_type=data.service
  app.cleaning_hours=parseInt(data.cleaning_hours)
  app.no_of_slots=Math.ceil(data.cleaning_hours/2)
  app.evaluation_book_id=data.evaluation_book_id
  app.schedule_id=data.id
  app.reducing_total=parseInt(data.estimated_cost)
  app.cleaning_start_date=data.cleaning_start_date
  app.selected_cleaning_date=data.cleaning_start_date
 
}

//load cleaning team data
function load_cleaning_team(visitcount,scheduleid,bookid){
  var visitcount = app.getCount(visitcount);
 app.selected_team=[]
 app.filtered_teams=[]
 app.temp_selected_item=[]
  axios.get(url+'/api/cleaning-team-data/',{ params: { 'visit_count':visitcount, 'schedule_id': scheduleid } })
              .then(function (response) {
                 
                  if (response.data.success == true){  
                      $('#visit_count_'+bookid).text(response.data.visit_count);
                      app.visit_count=parseInt(response.data.visit_count)
                      app.team_schedule_id=response.data.schedule_id
                      
                      if (response.data.cleaning_status == 'CLEANING_TEAM_ASSIGNED'){   
                          $('#check_in_out_'+bookid).hide();
                          $('#team_edit_url_'+bookid).attr('hidden',false);
                          $('#team_edit_url_'+bookid).attr('href','/common/editcleaning/team/'+scheduleid+'');
                          $('#status_dot'+bookid).html('<div class="status-dot assigned-chip-bg"></div><div>Team Assigned</div>');
                          console.log($('.team_edit_url2').attr('hidden'),$('.team_edit_url2').attr('href'),"attr")
                          
                          //backup
                          if(response.data.backup_start_at)
                          {
                            $('#id_backup_startat_'+bookid).text(response.data.backup_start_at);
                            $('#id_backupadd_'+bookid).hide();
                          }
                          else
                          {
                            $('#id_backup_startat_'+bookid).text('');
                            $('#id_backupadd_'+bookid).show();
                          }

                          if(response.data.backup_end_at)
                          {
                            $('#id_backup_endat_'+bookid).text(response.data.backup_end_at);
                          }
                          else
                          {
                            $('#id_backup_endat_'+bookid).text('');
                          }

                          if(response.data.backup_check_in)
                          {
                            $('#id_backup_checkin_'+bookid).text(response.data.backup_check_in);
                          }
                          else
                          {
                            $('#id_backup_checkin_'+bookid).text('');
                          }

                          if(response.data.backup_check_out)
                          {
                            $('#id_backup_checkout_'+bookid).text(response.data.backup_check_out);
                          }
                          else
                          {
                            $('#id_backup_checkout_'+bookid).text('');
                          }

                        }
                      else if(response.data.cleaning_status == 'CLEANING_IN_PROGRESS'){
                          $('#check_in_out_'+bookid).show();
                          $('#checkout_'+bookid).hide();

                          $('#id_check_in_'+bookid).text(response.data.start_at);
                          $('#id_check_in_notes'+bookid).text(response.data.checkin_notes);
                          $('#team_edit_url_'+bookid).attr('hidden',true);
                          $('#status_dot'+bookid).html('<div class="status-dot inprogress-chip-bg"></div><div>In Progress</div>');

                          $('#id_backup_startat_'+bookid).text();
                          $('#id_backup_endat_'+bookid).text();
                          $('#id_backup_checkin_'+bookid).text();
                          $('#id_backup_checkout_'+bookid).text();

                          //backup
                          if(response.data.backup_start_at)
                          {
                            $('#id_backup_startat_'+bookid).text(response.data.backup_start_at);
                            $('#id_backupadd_'+bookid).hide();
                          }
                          else
                          {
                            $('#id_backup_startat_'+bookid).text('');
                            $('#id_backupadd_'+bookid).show();
                          }

                          if(response.data.backup_end_at)
                          {
                            $('#id_backup_endat_'+bookid).text(response.data.backup_end_at);
                          }
                          else
                          {
                            $('#id_backup_endat_'+bookid).text('');
                          }

                          if(response.data.backup_check_in)
                          {
                            $('#id_backup_checkin_'+bookid).text(response.data.backup_check_in);
                          }
                          else
                          {
                            $('#id_backup_checkin_'+bookid).text('');
                          }

                          if(response.data.backup_check_out)
                          {
                            $('#id_backup_checkout_'+bookid).text(response.data.backup_check_out);
                          }
                          else
                          {
                            $('#id_backup_checkout_'+bookid).text('');
                          }

                        }
                      else if(response.data.cleaning_status == 'CLEANING_FULFILLED'){
                        $('#check_in_out_'+bookid).show();
                        $('#checkout_'+bookid).show();
                        
                        $('#id_check_in_'+bookid).text(response.data.start_at);
                        $('#id_check_out_'+bookid).text(response.data.end_at);
                        $('#id_check_in_notes'+bookid).text(response.data.checkin_notes);
                        $('#id_check_out_notes'+bookid).text(response.data.checkout_notes);
                        $('#team_edit_url_'+bookid).attr('hidden',true);
                        $('#status_dot'+bookid).html('<div class="status-dot completed-chip-bg"></div><div>Completed</div>');
                      
                        //backup
                        if(response.data.backup_start_at)
                        {
                          $('#id_backup_startat_'+bookid).text(response.data.backup_start_at);
                          $('#id_backupadd_'+bookid).hide();
                        }
                        else
                        {
                          $('#id_backup_startat_'+bookid).text('');
                          $('#id_backupadd_'+bookid).show();
                        }

                        if(response.data.backup_end_at)
                        {
                          $('#id_backup_endat_'+bookid).text(response.data.backup_end_at);
                        }
                        else
                        {
                          $('#id_backup_endat_'+bookid).text('');
                        }

                        if(response.data.backup_check_in)
                        {
                          $('#id_backup_checkin_'+bookid).text(response.data.backup_check_in);
                        }
                        else
                        {
                          $('#id_backup_checkin_'+bookid).text('');
                        }

                        if(response.data.backup_check_out)
                        {
                          $('#id_backup_checkout_'+bookid).text(response.data.backup_check_out);
                        }
                        else
                        {
                          $('#id_backup_checkout_'+bookid).text('');
                        }
                      }
                      else{
                        $('#check_in_out_'+bookid).hide();
                      }
                      
                      //team members
                      $('#id_team_members_div_'+bookid).empty();

                      $('#id_team_members_div_'+bookid).append('<div class="col-md-3 m-mt20 .c-mb-10 mr-0 ml-0"> <div class="row"> <div class="col-xs-4 pr-0"> <img class="clean-team-profile-pic" src="'+response.data.team_leader_image+'"> </div> <div class="col-xs-8"> <div class="order-agent-content text-left"> <h2>'+response.data.team_leader+'</h2> <h6>Cleaning Agent</h6> </div></div></div></div>');

                      $.each(response.data.members,function(key,value){
                          $('#id_team_members_div_'+bookid).append('<div class="col-md-3 m-mt20 .c-mb-10 mr-0 ml-0"> <div class="row"> <div class="col-xs-4 pr-0"> <img class="clean-team-profile-pic" src="'+value.member_image+'"> </div> <div class="col-xs-8"> <div class="order-agent-content text-left"> <h2>'+value.member_name+'</h2> <h6>Team Member</h6> </div></div></div></div>');
                      })

                      //backup members
                      $('#id_team_backupmembers_div_'+bookid).empty();
                      
                      $.each(response.data.backup_members,function(key,value){
                          $('#id_team_backupmembers_div_'+bookid).append('<div class="col-md-3 m-mt20 .c-mb-10 mr-0 ml-0"> <div class="row"> <div class="col-xs-4 pr-0"> <img class="clean-team-profile-pic" src="'+value.profile_image+'"> </div> <div class="col-xs-8"> <div class="order-agent-content text-left"> <h2>'+value.name+'</h2> <h6>Team Member</h6> </div></div></div></div>');
                      })


                      $('#id_assigned_by_'+bookid).text(response.data.assigned_by);
                      $('#id_assigned_by_img'+bookid).attr("src",response.data.assigned_by_image);
                      $('#id_assigned_by_usertype'+bookid).text(response.data.assigned_by_usertype);


                      
                      $('#id_cleaning_before_images_'+bookid).empty();
                      $('#id_cleaning_after_images_'+bookid).empty();

                      //hiding and showing image divs if images exist
                      if (response.data.before_cleaning_media.length == 0 && response.data.after_cleaning_media.length == 0){
                          $('#id_cleaning_images_'+bookid).hide();
                      }else{
                          $('#id_cleaning_images'+bookid).show();
                      }

                      if (response.data.before_cleaning_media.length == 0){
                          $('#id_cleaning_before_div_'+bookid).hide();
                      } else{
                          $('#id_cleaning_before_div_'+bookid).show();
                      }

                      if (response.data.after_cleaning_media.length == 0){
                          $('#id_cleaning_after_div_'+bookid).hide();
                      } else{
                          $('#id_cleaning_after_div_'+bookid).show();
                      }

                      //looping before cleaning images
                      
                      $.each(response.data.before_cleaning_media,function(key,value){
                          
                          $('#id_cleaning_before_images_'+bookid).append('<div> <img class="slider-img pointer" onclick="onClick(this)" src="'+value.before_cleaning_url+'" alt=""></div>');
                      })

                      //looping after cleaning images
                      $.each(response.data.after_cleaning_media,function(key,value){

                          $('#id_cleaning_after_images_'+bookid).append('<div><img class="slider-img pointer" onclick="onClick(this)" src="'+value.after_cleaning_url+'" alt=""></div>');
                      })  
                      $('.owl-carousel').trigger('destroy.owl.carousel');
                      $(".owl-carousel").owlCarousel({
                          items: 2,
                          nav: true,
                          margin: 10,
                          navText: [
                          `<i class='fa fa-chevron-left service-control' @click='prevService()'></i>`,
                          `<i class='fa fa-chevron-right service-control'></i>`,
                          ],
                      });
                      
                      //view ticket
                      if (response.data.followup_id === null){
                          $('#id_view_ticket_'+bookid).hide();
                      }else{
                          $('#id_view_ticket_'+bookid).show();
                          $('#id_view_ticket_'+bookid).attr('href','/common/ticket/details/'+response.data.customer_id+'/'+response.data.followup_id+'')
                      }

                      // //mark selected visit
                      $('.cleaning-status-row').removeClass('visit-border');
                      $('#id_select_visit_inner'+response.data.schedule_id+'').addClass('visit-border');

                  }else{
                      console.log("no data")
                  }; 
              })
}

function addSection(service){
  app.service_type=$(service).data('service')
  console.log("called add section"+app.service_type)

  if(app.service_type=='Window Cleaning'){
    app.getTheSize('Window Cleaning')
  }
  app.editSectionData=
    {
      "section_name":"",
      "size":"",
      "wall_type":[],
      "ceiling_type":[],
      "floor_type":[],
      "cement_residue":false,
      "section_cost":"",
      "section_net_cost":"",
      "sectiononly_cost":"",
      "sectiononly_net_cost":"",
      "keynotes":[],
      "addons":[],
      "new_kitchen":false,
      "is_cabinet":false,
     "is_highprice_facade":false,
     "is_highprice_window":false,
  }
 app.kitchen_keynotes=[]
 app.other_keynotes=[]
  app.action_type="Add"
  app.getAddons()
  app.getProductivity()
  $('#edit-dialog-tigger').click()
}
function editNotes(serviceDetails){
  app.action_type='evaluationbook_note'
  var note=$(serviceDetails).data('note')
  app.eval_book_id=$(serviceDetails).data('book_id')
  app.notes=note
  $('#notes-tigger').click()
}
const app = new Vue({
  el: "#app",
  
  delimiters: ["<%", "%>"],
  
  mounted() {
   this.url=api
   
    this.getOrderId()
    this.setDate(moment().format('MM/DD/YYYY'))
    this.selected_date=moment().format('DD-MM-YYYY')
    $('#date_hidden').val(moment().format('MM/DD/YYYY'))
    this.getTheSize('Kitchen Cleaning')
    
    console.log("service is"+$('.service-name'))
    var service=$('.service-name')
    var book_ids=$('.service_id')
    console.log("book ids ae"+JSON.stringify(book_ids))
    for(var i=0;i<service.length;i++)
    {
      if(!this.serviceExist($(book_ids[i]).val()))
      {
      var serid=$(book_ids[i]).val()
      var status=$('#service_status_'+serid).val()
      this.services.push({
        id:$(book_ids[i]).val(),
        name:$(service[i]).text(),
        status:status
      })
      if(status!='CANCELLED')
      {
      this.services_options.push({
        id:$(book_ids[i]).val(),
        name:$(service[i]).text(),
        status:status
      })
    }
    }
    }
    
   
    
  },
  components: { Multiselect: window.VueMultiselect.default },

  data: {
    cancelledAmount:0,
    new_count:0,
    taken_status:'AGENT_TAKEN',
    image_eval_id:null,
    kitchen_msg:false,
    keynote_msg:false,
    addon_msg:false,
    window_size:[],
    addon_size_data:{},
    newaddon_quantity:'',
    selected_addon:'',
    
    priceupdate:true,
    customer_note:'',
    notes:'',
    reload:true,
    all_val:false,
    reduction_status:false,
    no_of_visits:0,
    services:[],
    reducing_total:0,
    selected_cleaning_date:'',
    cleaning_policy:'',
    highprice_facade:[],
    lowprice_facade:[],
    highprice_window:[],
    lowprice_window:[],
    services_options:[],
    fixed_section_cost:null,
    soltdate: null, 
    edit: false,
    cancelDialog:false,
    editSectionDialog:false,
    year:null,
    day:null,
    month:null,
    paymentType:"",
    key: "",
    breakDownFlag:false,
    amount:"",
    contacts:[],
    sectionData:{},
    value: [],
    floor_type:'',
    wall_type:'',
    ceiling_type:'',
    service_type:'',
    currentServiceType:'',
    service_productivity:[],
    selected_size:{},
    cause_of_stain:['INK MARK', 'HARD DUST', 'COFFEE & TEA SPILL', 'OIL','GREASE', 'PAINT', 'URINE', 'MILK SPILL', 'NO STAIN', 'OTHERS'],
    walltypes:["BRICKS","GLASS","CONCRETE","CERAMIC","GYPSUM","FABRIC","RUBBER","STONE","TERRAZO","STAINLESS","VINYL","WOODEN","OTHERS"],
    ceilingtypes:["WOODEN","GLASS","CONCRETE","CERAMIC","GYPSUM","FOAM","PLASTIC","FABRIC","RUBBER","STAINLESS","VENYL","OTHERS"],
    floortypes:["MARBLE","GLASS","STONE","CERAMIC","CONCRETE","BRICKS","WOODEN","TERRAZO","OTHERS"],
    materials:["POLYESTER","NATURAL FIBER","SYNTHETIC","LEATHER","OLEFIN","POLYPROPYLENE","NYLON"],
    colors:["GREEN","SILVER","VIOLET","WHITE","BLACK","BEIGE","BLUE","GREY","RED","CREAM","MULTI","OFF WHITE","MEROON","ORANGE","PINK","GOLD","BROWN","YELLOW","ROYAL BLUE","LILAC","OTHERS"],
    
             productivity:{},
             editSectionData:{
              size:{},
             keynotes:[],
              section_cost:0,
              section_name:'',
              floor_type:[],
              ceiling_type:[],
              wall_type:[],
              material:[],
              category:'Floor',
              age:null,
              new_kitchen:false
             },
             section_cost:0,
             orderId:'',
             sections:[],
             currentSection:[],
             gotSection:false,
           
             eval_book_id:'',
             action_type:'',
             paymentData:{
               discount:'',
               additional_charge:'',
               amount_before_cleaning:'',
               amount_after_cleaning:'',
               amount:'',
               payment_method:''
             },
             total_amount:0,
             deleteSectionData:{
               section_id:''
             },
             no_of_cleaners:0,
             schedule_serviceTypes:[],
             timeSlots:{},
             selectedSlots:[],
             selected_slots:{},
             cleaning_hours:null,
             no_of_cleaners:null,
             no_of_slots:0,
             selected_date:'',
             evaluation_book_id:'',
             slotFormat:{
              "1":{
                start_time:'12:00 AM',
                end_time:'02:00 AM'
              },
              "2":{
                start_time:'02:00 AM',
                end_time:'04:00 AM'
              },
              "3":{
                start_time:'04:00 AM',
                end_time:'06:00 AM'
              },
              "4":{
                start_time:'06:00 AM',
                end_time:'08:00 AM'
              },
              "5":{
                start_time:'08:00 AM',
                end_time:'10:00 AM'
              },
              "6":{
                start_time:'10:00 AM',
                end_time:'12:00 PM'
              },
              "7":{
                start_time:'12:00 PM',
                end_time:'02:00 PM'
              },
              "8":{
                start_time:'02:00 PM',
                end_time:'04:00 PM'
              },
              "9":{
                start_time:'04:00 PM',
                end_time:'06:00 PM'
              },
              "10":{
                start_time:'06:00 PM',
                end_time:'08:00 PM'
              },
              "11":{
                start_time:'08:00 PM',
                end_time:'10:00 PM'
              },
              "12":{
                start_time:'10:00 PM',
                end_time:'12:00 AM'
              }
            },
            parsedTimeSlots:[],
            available_slotes:[],
            selected_no_of_cleaners:null,
            visit_err:'',
            cleaning_action:'',
            cleaning_start_date:'',
            schedule_id:'',
            newkeynote:{
              sub_area:'',
              quantity:''
            },
            newkitchenkeynote:{
              
              size:'',
              type:'old',
              residue:false,
              is_cabinet:false,
            },
            keynote_update:true,
            addon_update:true,
            kitchen_size:[],
            new_kitchen_size:[],
            old_kitchen_size:[],
            new_kitchen_cabinet_size:[],
            old_kitchen_cabinet_size:[],
            new_kitchen_nocabinet_size:[],
            old_kitchen_nocabinet_size:[],
            kitchen_keynotes:[],
            other_keynotes:[],
            addons:[],
            kitchen_addons:[],
            final_keynotes:[],
            service_size:[],
            chair_size:[],
            sofa_size:[],
           progress:20,
           slotloader:false,
            services_list:[],
          url:'',
          addons_parsed:[],
          image_url:'',
          image_urls:[],
          media_file:'',
          media_files:[],
          visit_count:0,
          imageForm:new FormData(),
          break_act:false,
          two_counter:0,
          team:[],
          
          team_search:'',
          team_options:false,
          team_cleaning_start:'',
          team_cleaning_end:'',
          team_cleaning_hr:'',
          cleaning_team_api:false,
          date_options:[],
          time_options:[],
          selected_team:[],
          temp_selected_item:[],
          team_cleaning_id:'',
          backup_team_data:{
            cleaning_date_start:'',
            cleaning_time_start:'',
            cleaning_time_end:'',
            cleaning_date_end:'',
            service_types:[]
          },
          filtered_teams:[],
          current_backups:[],
          visit_count:'',
          team_schedule_id:''
         // url:'http://localhost:8000'
      // url:'https://test.bleach-kw.com'
            //url:'http://127.0.0.1:8000'
  },
  methods:{
    
    getTeamMembers(){
      axios.post(this.url+'/customer/availablecleaners/',{
        cleaning_datetime_start:this.backup_team_data.cleaning_date_start+' '+this.backup_team_data.cleaning_time_start,
        cleaning_datetime_end:this.backup_team_data.cleaning_date_end+' '+this.backup_team_data.cleaning_time_end,
        service_types:['General Cleaning']

      }).then(response=>{
        this.team=response.data.available_cleaners
        this.filtered_teams=[...this.team]
      }).catch(err=>{

      })
    },
    searchTeam(){
      var filtered=[]
      if(!this.team_search){
        this.filtered_teams=this.team
      }
      for(var i=0;i<this.team.length;i++){
        var search=this.team_search.toUpperCase()
        var teamname=this.team[i].name.toUpperCase()
        if(teamname.startsWith(search)){
          filtered.push(this.team[i])
        }
      }
      this.filtered_teams=[ ...filtered ]
    },  
    selectTeam(){
    this.selected_team=[ ...this.temp_selected_item ]
    this.team_options=false
    this.team_search=''
    this.filtered_teams=[ ...this.team ]
    },
    addTeamMembers(){
      var backup_cleaners=[]
      for(var i=0;i<this.selected_team.length;i++){
        backup_cleaners.push(this.selected_team[i].id)
      }
      axios.post(this.url+'/customer/editorder/'+this.orderId,{
        action_type:'add_backupteam',
        backup_start_at:this.backup_team_data.cleaning_date_start+' '+this.backup_team_data.cleaning_time_start,
        backup_end_at:this.backup_team_data.cleaning_date_end+' '+this.backup_team_data.cleaning_time_end,
        backup_cleaners :backup_cleaners,
        team_id:this.team_cleaning_id

      }).then(response=>{
        $('#close_backup').click()
        location.reload()
      })
    },
    editTeamMembers(){
      var backup_cleaners=[]
      for(var i=0;i<this.selected_team.length;i++){
        backup_cleaners.push(this.selected_team[i].id)
      }
      axios.post(this.url+'/customer/editorder/'+this.orderId,{
        action_type:'edit_backupteam',
        backup_start_at:this.backup_team_data.cleaning_date_start+' '+this.backup_team_data.cleaning_time_start,
        backup_end_at:this.backup_team_data.cleaning_date_end+' '+this.backup_team_data.cleaning_time_end,
        backup_cleaners :backup_cleaners,
        team_id:this.team_cleaning_id

      }).then(response=>{
        $('#close_backup').click()
        location.reload()
      })
    },
    removeTeam(index){
      this.selected_team.splice(index,1)
      this.temp_selected_item.splice(index,1)
    },
    getStartDates(){
      var start_dates=[]
      for(var i=0;i<this.date_options.length;i++){
          start_dates.push(this.date_options[i].date)
      }
      return start_dates
    },
    getEndDates(){
      var end_dates=[]
      for(var i=0;i<this.date_options.length;i++){
        if(moment(this.backup_team_data.cleaning_date_start,'DD-MM-YYYY').isSameOrBefore(moment(this.date_options[i].date,'DD-MM-YYYY')))
        end_dates.push(this.date_options[i].date)
    }
    return end_dates
    },
    getStartTime(){
      var start_time=[]
      for(var i=0;i<this.date_options.length;i++){
        if(this.date_options[i].date==this.backup_team_data.cleaning_date_start){
          // for(var j=0;j<this.date_options[i].length;j++){
          //   this.backup_team_data.cleaning_date_start
          // }
          return this.date_options[i].time
        }
         
      }
      
    },
    getEndTime(){
      var end_time=[]
      for(var i=0;i<this.date_options.length;i++){
        if(this.date_options[i].date==this.backup_team_data.cleaning_date_end){
           for(var j=0;j<this.date_options[i].time.length;j++){
             if(moment(this.date_options[i].time[j],'hh:mm a').isAfter(moment(this.backup_team_data.cleaning_time_start,'hh:mm a'))){
               end_time.push(this.date_options[i].time[j])
             }
            
           }
           var added_time=moment(this.date_options[i].time[this.date_options[i].time.length-1],'hh:mm a').add(2,'hours').format('hh:mm a')
           end_time.push(added_time)
          
        }
         
      }
     
      return end_time
    },
 async addBackupTeam(team_id,id,start,end,duration){
    console.log("start:"+start+"end:"+end+"duartion:"+duration+"team id is "+team_id)
    var team=await this.loadBackupTeamToAdd(this.visit_count,this.team_schedule_id)
   if(!this.cleaning_team_api){
     this.team_cleaning_id=team_id
    this.team_cleaning_start=start
    this.team_cleaning_end=end
    this.team_cleaning_hr=duration
   }
   this.backup_team_data.cleaning_date_start=moment(this.team_cleaning_start,'DD-MM-YYYY hh:mm a').format('DD-MM-YYYY')
   this.backup_team_data.cleaning_time_start=moment(this.team_cleaning_start,'DD-MM-YYYY hh:mm a').format('hh:mm a')
   this.backup_team_data.cleaning_date_end=moment(this.team_cleaning_end,'DD-MM-YYYY hh:mm a').format('DD-MM-YYYY')
   this.backup_team_data.cleaning_time_end=moment(this.team_cleaning_end,'DD-MM-YYYY hh:mm a').format('hh:mm a')
   this.date_options=[]
  var start_date=moment(this.team_cleaning_start,'DD-MM-YYYY hh:mm a')
  var end_date=moment(this.team_cleaning_end,'DD-MM-YYYY hh:mm a')
  var count=0
  console.log("start:"+this.team_cleaning_start+"end:"+this.team_cleaning_end+"duartion:"+this.team_cleaning_hr+"id is "+id)
   while(moment(this.team_cleaning_start,'DD-MM-YYYY hh:mm a').isSameOrBefore(moment(this.team_cleaning_end,'DD-MM-YYYY hh:mm a')) && count<parseInt(this.team_cleaning_hr))
   {
     var found=false
     for(var i=0;i<this.date_options.length;i++){
       if(this.date_options[i].date==moment(this.team_cleaning_start,'DD-MM-YYYY hh:mm a').format('DD-MM-YYYY')){
          found=true
          this.date_options[i].time.push(moment(this.team_cleaning_start,'DD-MM-YYYY hh:mm a').format('hh:mm a'))
          break
       }
     }
     if(!found)
     {
     this.date_options.push(
      {
        date:moment(this.team_cleaning_start,'DD-MM-YYYY hh:mm a').format('DD-MM-YYYY'),
        time:[moment(this.team_cleaning_start,'DD-MM-YYYY hh:mm a').format('hh:mm a')]
      }) 
     
     }
     this.team_cleaning_start= moment(this.team_cleaning_start,'DD-MM-YYYY hh:mm a').add(2,'hours').format('DD-MM-YYYY hh:mm a')
     count=count+2

   }
   console.log("date options"+this.date_options)
  this.getTeamMembers()
  $('#backupTeamBtn').click()
 },
 async loadBackupTeamToAdd(visitcount,scheduleid){
  await axios.get(url+'/api/cleaning-team-data/',{ params: { 'visit_count':visitcount, 'schedule_id': scheduleid } }).then(response=>{
                     this.cleaning_team_api=true
                      this.team_cleaning_start=response.data.cleaning_start_at
                      this.team_cleaning_end=response.data.cleaning_end_at
                      this.team_cleaning_hr=response.data.cleaning_hours
                      this.team_cleaning_id=response.data.team_id
                     

                    
  }).catch(err=>{

  })
  return true
 },
 async loadBackupTeam(visitcount,scheduleid){
  await axios.get(url+'/api/cleaning-team-data/',{ params: { 'visit_count':visitcount, 'schedule_id': scheduleid } }).then(response=>{
                     this.cleaning_team_api=true
                      this.team_cleaning_start=response.data.backup_datetime_start_at
                      this.team_cleaning_end=response.data.backup_datetime_end_at
                      this.team_cleaning_hr=response.data.cleaning_hours
                      this.team_cleaning_id=response.data.team_id
                      this.current_backups=response.data.backup_members

                    
  }).catch(err=>{

  })
  return true
 },
 async editBackupTeam(order_id,team_id,id,start,end,duration,cleaning_team){
   console.log("cleaning tem:"+cleaning_team)
   if(!this.visit_count){
     this.visit_count=1
   }
   if(!this.team_schedule_id){
     this.team_schedule_id=order_id
   }
   var team=await this.loadBackupTeam(this.visit_count,this.team_schedule_id)
   console.log("current backups is"+this.current_backups)
  this.selected_team=[ ...this.current_backups ]
  this.temp_selected_item=[ ...this.current_backups ]
  if(!this.cleaning_team_api){
    this.team_cleaning_id=team_id
   this.team_cleaning_start=start
   this.team_cleaning_end=end
   this.team_cleaning_hr=duration
  }
  this.backup_team_data.cleaning_date_start=moment(this.team_cleaning_start,'DD-MM-YYYY hh:mm a').format('DD-MM-YYYY')
  this.backup_team_data.cleaning_time_start=moment(this.team_cleaning_start,'DD-MM-YYYY hh:mm a').format('hh:mm a')
  this.backup_team_data.cleaning_date_end=moment(this.team_cleaning_end,'DD-MM-YYYY hh:mm a').format('DD-MM-YYYY')
  this.backup_team_data.cleaning_time_end=moment(this.team_cleaning_end,'DD-MM-YYYY hh:mm a').format('hh:mm a')
  this.date_options=[]
 var start_date=moment(this.team_cleaning_start,'DD-MM-YYYY hh:mm a')
 var end_date=moment(this.team_cleaning_end,'DD-MM-YYYY hh:mm a')
 var count=0
 console.log("start:"+start_date+"end:"+end_date+"duartion:"+duration+"id is "+id)
  while(moment(this.team_cleaning_start,'DD-MM-YYYY hh:mm a').isSameOrBefore(moment(this.team_cleaning_end,'DD-MM-YYYY hh:mm a')) && count<parseInt(this.team_cleaning_hr))
  {
    var found=false
    for(var i=0;i<this.date_options.length;i++){
      if(this.date_options[i].date==moment(this.team_cleaning_start,'DD-MM-YYYY hh:mm a').format('DD-MM-YYYY')){
         found=true
         this.date_options[i].time.push(moment(this.team_cleaning_start,'DD-MM-YYYY hh:mm a').format('hh:mm a'))
         break
      }
    }
    if(!found)
    {
    this.date_options.push(
     {
       date:moment(this.team_cleaning_start,'DD-MM-YYYY hh:mm a').format('DD-MM-YYYY'),
       time:[moment(this.team_cleaning_start,'DD-MM-YYYY hh:mm a').format('hh:mm a')]
     }) 
    
    }
    this.team_cleaning_start= moment(this.team_cleaning_start,'DD-MM-YYYY hh:mm a').add(2,'hours').format('DD-MM-YYYY hh:mm a')
    count=count+2

  }
  console.log("date options"+this.date_options)
 this.getTeamMembers()
  $('#editBackupTeamBtn').click()
},
    getCount(sch_id){
     
     $('#'+sch_id+'-count').html($("#"+sch_id).index()+1)

     return($("#"+sch_id).index()+1);
    },
    async onImageFileChanged(event) {
    
  
    
      
      var files=event.target.files
  
    
     for(var i=0;i<files.length;i++){
       this.image_urls.push(URL.createObjectURL(files[i]))
      this.media_files.push(files[i])
      }
   
  
    
    
    },
    delImage(index){
      this.image_urls.splice(index,1)
      this.media_files.splice(index,1)
    },
    findKitchenSize(name,cabinet,type){
      console.log("name is"+name+"cabinet is"+cabinet+"type is"+type)
      if(type=='new' && cabinet){
        
        for(var i=0;i<this.new_kitchen_cabinet_size.length;i++){
          if(this.new_kitchen_cabinet_size[i].name==name){
           
            return this.new_kitchen_cabinet_size[i]
          }
        }
      }
      else if(type=='new' && !cabinet){
       
        for(var i=0;i<this.new_kitchen_nocabinet_size.length;i++){
          if(this.new_kitchen_nocabinet_size[i].name==name){
          
            return this.new_kitchen_nocabinet_size[i]
          }
        }
      }
      else if(type=='old' && cabinet){
       
        for(var i=0;i<this.old_kitchen_cabinet_size.length;i++){
          if(this.old_kitchen_cabinet_size[i].name==name){
            
            return this.old_kitchen_cabinet_size[i]
          }
        }
      }
      else if(type=='old' && !cabinet){
       
        for(var i=0;i<this.old_kitchen_nocabinet_size.length;i++){
          if(this.old_kitchen_nocabinet_size[i].name==name){
            
            return this.old_kitchen_nocabinet_size[i]
          }
        }
      }
    },
    changeCurrentAddons(){
      this.selected_addon.details.price=this.selected_addon.selected_size.price
      this.selected_addon.details.category=this.selected_addon.selected_size.size
    },

    addToAddon(){
      if(this.newaddon_quantity && this.selected_addon)
      {
        this.addon_msg=false
      this.kitchen_addons.push({
        name:this.selected_addon.details.name,
        addon_cost:this.selected_addon.details.price,
        addon_net_cost:this.selected_addon.details.price*parseInt(this.newaddon_quantity),
        quantity:parseInt(this.newaddon_quantity),
        size:'',
        other_details:''
      })
      this.recalcAddonCost()
      this.newaddon_quantity=''
      this.selected_addon=''
    }
    else{
      this.addon_msg=true
    }
    },
    updateAddon(index){
      this.kitchen_addons[index].addon_net_cost=parseInt(this.kitchen_addons[index].quantity)*this.kitchen_addons[index].addon_cost
      this.recalcAddonCost()
    },
    async getAddons(){
      this.addons=[]
      var ser = 'Kitchen Cleaning'
      axios.get(this.url+'/customer/ajax/getserviceaddons?service_type='+ser).then(response=>{
        this.addons=response.data.service_addons
       this.parseAddons()
       
      }).catch((error)=>{
        console.log(error)
      })
    },
    findAddons(addon){
  
      for(var i=0;i<this.addons_parsed.length;i++){
        if(this.addons_parsed[i].details.name==addon){
          return i
        }
      }
      return 'not found'
    },
    async parseAddons(){
      this.addons_parsed=[]
      for(var i=0;i<this.addons.length;i++){
        if(this.addons[i].category){
          
        
          var add_on_stat=this.findAddons(this.addons[i].name)
          if(!this.addon_size_data[this.addons[i].name]){
            
          
            this.addon_size_data[this.addons[i].name]=[]
          }
          if(add_on_stat!='not found'){
            this.addons_parsed[add_on_stat].size.push({
              size:this.addons[i].category,
              max_size:this.addons[i].size,
              price:this.addons[i].price
            })
            this.addon_size_data[this.addons[i].name].push({
              size:this.addons[i].category,
              max_size:this.addons[i].size,
              price:this.addons[i].price
            
          })
          }
          else{
          
            
          this.addons_parsed.push({
            details:this.addons[i],
            selected:false,
            quantity:0,  
            size:[{
              size:this.addons[i].category,
              max_size:this.addons[i].size,
              price:this.addons[i].price
            }],
            selected_size:""
          })
          this.addon_size_data[this.addons[i].name].push({
              size:this.addons[i].category,
              max_size:this.addons[i].size,
              price:this.addons[i].price
            
          })
        
        }
        }
        else{
        this.addons_parsed.push({
          details:this.addons[i],
          selected:false,
          quantity:0,
          
          size:[],
          selected_size:""
        })
      }
       
  
      }},
    serviceExist(id){
      for(var k=0;k<this.services.length;k++){
        if(this.services[k].id==id){
          return true
        }
      }
      return false

    },
   checkAll(){
    if(this.all_val){
        this.services_list=this.services_options
    }
    else{
      this.services_list=[]
    }
   },
   cancelServiceOrder(){
     var service_books=[]
     var requester_id=$('#user_id').val()
     for(var i=0;i<this.services_list.length;i++){
       service_books.push(this.services_list[i].id)
     }
    axios.post(this.url+'/customer/service/cancellrequest/',{
      service_books:service_books,
      requester_id:requester_id
    }).then(response=>{

      this.$notify({
        group: 'message',
        title: 'Cancellation Request Sent sucessfully',
        text: '',
        type:'success'
        
      });
      var delayInMilliseconds = 2000; //1 second

setTimeout(function() {
  location.reload()
}, delayInMilliseconds);
     
      
      
    })
   },
   salesadminCancelServiceOrder(){
    var service_books=[]
    var requester_id=$('#user_id').val()
    for(var i=0;i<this.services_list.length;i++){
      service_books.push(this.services_list[i].id)
    }
   axios.post(this.url+'/customer/service/cancellrequest/',{
     service_books:service_books,
     requester_id:requester_id
   }).then(response=>{

    $('#salesadmin-redirect').click()
     
     
   })
   },
   bookingofficerCancelServiceOrder(){
    var service_books=[]
    var requester_id=$('#user_id').val()
    for(var i=0;i<this.services_list.length;i++){
      service_books.push(this.services_list[i].id)
    }
   axios.post(this.url+'/customer/service/cancellrequest/',{
     service_books:service_books,
     requester_id:requester_id
   }).then(response=>{
    $('#bookingofficer-redirect').click()
     
     
   })
   },
   removeAll(){
     
    if(this.services_options.length==this.services_list.length){
      this.all_val=true
    }
    else{
      this.all_val=false
    }
   },
    getTheSize(service){
      var service_productivity=[]
      if(service=='Hourly Cleaning'){
        service='General Cleaning'
      }
      axios.get(this.url+'/customer/ajax/getservicesizeprice?service_type='+service).then(response=>{
          this.productivity=response.data
          for(var i in this.productivity){
            
            service_productivity.push(this.productivity[i])
          }
          if(service=='Kitchen Cleaning'){
            this.kitchen_size=service_productivity
            this.formatKitchenSize()
          }
          if(service=='Window Cleaning'){
            this.window_size=service_productivity
            this.formatWindowSize()
          }
          
          
      })
    },
    removeInitialKitchenCost(){
      var totalKitchenCost=0
      for(var i=0;i<this.editSectionData.keynotes.length;i++){
        if(this.editSectionData.keynotes[i].sub_area=='kitchen'){
          var qty=JSON.parse(this.editSectionData.keynotes[i].quantity)
          totalKitchenCost=totalKitchenCost+qty.cost
          console.log("cost is"+qty.cost)
        }
      }
      this.fixed_section_cost=this.editSectionData.section_cost-totalKitchenCost
      console.log("fuixed cost is"+this.fixed_section_cost)
    },
    recalcKeynoteCost(){
      this.editSectionData.section_cost=this.fixed_section_cost
      console.log("called me"+JSON.stringify(this.kitchen_keynotes))
      for(var j=0;j<this.kitchen_keynotes.length;j++){
        if(this.service_type!='General Cleaning'){
        this.editSectionData.section_cost=this.editSectionData.section_cost+this.kitchen_keynotes[j].quantity.size.cost
        }
        else{
          if(this.kitchen_keynotes[j].other_details.type=='old'){
            this.editSectionData.section_cost=this.editSectionData.section_cost+this.kitchen_keynotes[j].quantity.size.cost
          }
        }
      }
    },
    addKitchenToKeynote(){
     
      this.kitchen_keynotes.push({
        sub_area:"kitchen",
        quantity:{
          size:this.newkitchenkeynote.size,
          max_size:this.newkitchenkeynote.size.max_size,
          type:this.newkitchenkeynote.type,
          residue:this.newkitchenkeynote.residue,
          cost:this.newkitchenkeynote.size.cost
        }
      })
      this.newkitchenkeynote={
        sub_area:'',
        quantity:{
          size:{},
          
          type:'old',
          residue:false,


        }
      }
      this.recalcKeynoteCost()
      
      
    },
    addKitchenToAddon(){
      if(this.newkitchenkeynote.size)
      {
        this.kitchen_msg=false
      this.kitchen_addons.push({
        addon_cost:this.newkitchenkeynote.size.cost,
        addon_net_cost:this.newkitchenkeynote.size.cost,
        name:'kitchen',
        quantity:"1",
        size:this.newkitchenkeynote.size.name,
        other_details:{
          is_cabinet:false,
          max_size:null,
          residue:this.newkitchenkeynote.residue,
          size:this.newkitchenkeynote.size,
          type:this.newkitchenkeynote.type

        }
      
      })
      this.newkitchenkeynote={
            residue:false,
            type:"old",
            is_cabinet:false,
            other_details:{},
            size:{}
        }
      
      this.recalcAddonCost()
      }
      else{
        this.kitchen_msg=true
      }
    },
    deleteKitchenFromAddon(index){
      this.kitchen_addons.splice(index,1)
      this.recalcAddonCost()
    },
    changeKitchenSize(index){
     
      this.kitchen_addons[index].addon_cost= this.kitchen_addons[index].other_details.size.cost
      this.kitchen_addons[index].addon_net_cost= this.kitchen_addons[index].other_details.size.cost
      
      this.kitchen_addons[index].size=this.kitchen_addons[index].other_details.size.name
      this.recalcAddonCost()
    },
    removeKitchen(index){
      this.kitchen_keynotes.splice(index,1)
      this.recalcKeynoteCost()
    },
    formatKitchenSize(){
      
      this.new_kitchen_cabinet_size=[]
      this.new_kitchen_nocabinet_size=[]
      this.old_kitchen_cabinet_size=[]
      this.old_kitchen_nocabinet_size=[]
      
        for(var i=0;i<this.kitchen_size.length;i++){
          this.kitchen_size[i].combined_size=this.kitchen_size[i].name+' ( '+this.kitchen_size[i].min_size+' sq.m - '+this.kitchen_size[i].max_size+' sq.m )'

          if(this.kitchen_size[i].is_newkitchen){
            if(this.kitchen_size[i].is_cabinet){
              this.new_kitchen_cabinet_size.push(this.kitchen_size[i])
            }else{
              this.new_kitchen_nocabinet_size.push(this.kitchen_size[i])
            }
         
          }
          else{
            if(this.kitchen_size[i].is_cabinet){
             this.old_kitchen_cabinet_size.push(this.kitchen_size[i])
            }
            else{
              this.old_kitchen_nocabinet_size.push(this.kitchen_size[i])
            }
          }
        }
        
      
    },

   /* formatFacadeSize(){
      
      this.highprice_facade=[]
      this.lowprice_facade=[]
      
        for(var i=0;i<this.service_productivity.length;i++){
         
          if(this.service_productivity[i].is_highprice_facade){
            this.highprice_facade.push(this.service_productivity[i])
          }
          else{
            this.lowprice_facade.push(this.service_productivity[i])
          }
        }
        
      
    },*/
    formatWindowSize(){
      this.highprice_window=[]
      this.lowprice_window=[]
      for(var i=0;i<this.window_size.length;i++){
        
        if(this.window_size[i].is_highprice_window){
          this.window_size[i].combined_size=this.window_size[i].name+' ( '+this.window_size[i].min_size+' sq.m - '+this.window_size[i].max_size+' sq.m )'
          this.highprice_window.push(this.window_size[i])
        }
        else{
          this.window_size[i].combined_size=this.window_size[i].name+' ( '+this.window_size[i].min_size+' sq.m - '+this.window_size[i].max_size+' sq.m )'
          this.lowprice_window.push(this.window_size[i])
        }
      }
        
      
    },
    addToKeynote(){
      if(this.newkeynote.sub_area && this.newkeynote.quantity)
      {
        this.keynote_msg=false
      this.keynote_update=false
      this.other_keynotes.push(this.newkeynote)
      this.keynote_update=true
      this.newkeynote={
        sub_area:'',
        quantity:''
      }
    }
    else{
      this.keynote_msg=true
    }
    },
    delKeynote(index){
      this.keynote_update=false
      this.other_keynotes.splice(index,1)
      this.keynote_update=true
    },
    delAddon(index){
      this.addon_update=false
      this.kitchen_addons.splice(index,1)
      this.addon_update=true
      this.recalcAddonCost()
    },
    checkSlot(index){
      if(!this.selected_slots[this.selected_date]){
        this.selected_slots[this.selected_date]=[]
      }
      if(this.dateContCheck() && this.selected_slots[this.selected_date].length<=0){
        if(index==0){
          return true
        }
        else{
          return false
        }
      }
      
      if(this.selected_slots[this.selected_date].length>0 ){
       
       var real_slot=this.available_slotes[index]
        var prevSlot=real_slot-1
        var nextSlot=real_slot+1
        if(this.available_slotes.includes(prevSlot) || this.available_slotes.includes(nextSlot)){
          var prevSlotIndex=this.available_slotes.indexOf(prevSlot)
          var nextSlotIndex=this.available_slotes.indexOf(nextSlot)
          
          if(nextSlotIndex>=0 && prevSlotIndex>=0)
          {
          if(this.selected_slots[this.selected_date].includes(this.findSlotIndex(prevSlotIndex))||this.selected_slots[this.selected_date].includes(this.findSlotIndex(nextSlotIndex))){
            return true
          }
          else{
            return false
          }
        }
        else{
          if(nextSlotIndex<0 && prevSlotIndex>0){
            if(this.selected_slots[this.selected_date].includes(this.findSlotIndex(prevSlotIndex))){
              return true
            }
            else{
              return false
            }
          }
          else if(prevSlotIndex<0 && nextSlotIndex>0){
            if(this.selected_slots[this.selected_date].includes(this.findSlotIndex(nextSlotIndex))){
              return true
            }
            else{
              return false
            }
          }
          
        }
      }
        else{
          return false
        }
         
        
      }
      else{
        return true
      }
    },
    selectSlot(index){
      this.reload=false
      this.selectedSlots.push(index)
      if(!this.selected_slots[this.selected_date])
      {
      this.selected_slots[this.selected_date]=[]
      }
      this.selected_slots[this.selected_date].push(this.findSlotIndex(index))
      this.reload=true
    },
    resetSlotsSelected(){
      this.selected_slots={}
      this.selected_slots[this.selected_date]=[]
      console.log("inside rest")
    },
    removeSlot(index){
      this.reload=false
      var slotindex=this.selectedSlots.indexOf(index)
      var slotindex2=this.selected_slots[this.selected_date].indexOf(this.findSlotIndex(index))
      this.selected_slots[this.selected_date].splice(slotindex2)
      this.selectedSlots.splice(slotindex,1)
      this.reload=true
    },
    countSelection(){
      var count=0
      for(var i in this.selected_slots){
        count=count+this.selected_slots[i].length
      }
      return count
    },
    findSlotIndex(index){
      for(var i in this.slotFormat){
        if(this.slotFormat[i].start_time==this.parsedTimeSlots[index].start_time){
          
          return i
          
        }
      }
    },
    dateContCheck(){
      var prevDate=moment(this.selected_date,'DD-MM-YYYY').subtract(1,"days").format('DD-MM-YYYY')
     
      if(this.selected_slots[prevDate]){
        if(this.selected_slots[prevDate].includes("12")){
          return true
        }
        else{
          return false
        }

      }
      else{
        return false
      }
    },
    parseOneTimeSlots(){
      this.parsedTimeSlots=[]
      this.available_slotes=[]
      for(var i in this.timeSlots){
        if(this.timeSlots[i].includes(2)){
          var slotNo=(parseInt(i)+2)/2
          this.available_slotes.push(slotNo)
          this.parsedTimeSlots.push(this.slotFormat[String(slotNo)])
          
          
        }
      }
    },
    getSlotes(date){
      var cont_check=this.dateContCheck()
      if(!cont_check){
        if(this.selected_slots[date]){
          if(!this.selected_slots[date].includes('12'))
            {
              this.selected_slots={}
              this.selected_slots[this.selected_date]=[]
            }
        }
        else{
          this.selected_slots={}
          this.selected_slots[this.selected_date]=[]
        }
       
      }
      this.schedule_serviceTypes=[]
      this.selectedSlots=[]
      this.schedule_serviceTypes.push(this.service_type)
      this.slotloader=true
      axios
      .post(
         this.url+"/customer/ajax/getmultipleservicecleaningslotes",{service_types:this.schedule_serviceTypes,cleaning_date:date,number_of_cleaners:this.selected_no_of_cleaners}
       
      )
      .then((response) => {
         this.timeSlots = response.data.slotes;
         this.parseOneTimeSlots()
         if(response.data.Error){
           this.errMsg=response.data['Error']
         }
         else{
           this.errMsg=''
         }
         this.slotloader=false
      

      })
       .catch((error) => {
        console.log(error);
      });
  
    },
    getSlotesByCleaners(){
      this.schedule_serviceTypes=[]
      this.selectedSlots=[]
      this.schedule_serviceTypes.push(this.service_type)
      this.slotloader=true
      if(!this.selected_cleaning_date){
        this.selected_cleaning_date=moment().format('DD-MM-YYYY')
      }
      axios
      .post(
         this.url+"/customer/ajax/getmultipleservicecleaningslotes",{service_types:this.schedule_serviceTypes,cleaning_date:this.selected_cleaning_date,number_of_cleaners:this.selected_no_of_cleaners}
       
      )
      .then((response) => {
         this.timeSlots = response.data.slotes;
         this.parseOneTimeSlots()
         if(response.data.Error){
           this.errMsg=response.data['Error']
         }
         else{
           this.errMsg=''
         }
         this.slotloader=false
      

      })
       .catch((error) => {
        console.log(error);
      });
  
    },
    getVisitSlotes(date){
      this.schedule_serviceTypes=[]
      this.selectedSlots=[]
      this.schedule_serviceTypes.push(this.service_type)
      this.slotloader=true
      axios
      .post(
         this.url+"/customer/ajax/getmultipleservicecleaningslotes",{service_types:this.schedule_serviceTypes,cleaning_date:date,number_of_cleaners:this.selected_no_of_cleaners}
       
      )
      .then((response) => {
        this.slotloader=false
         this.timeSlots = response.data.slotes;
         this.parseOneTimeSlots()
         if(response.data.Error){
           this.errMsg=response.data['Error']
         }
         else{
           this.errMsg=''
         }
      

      })
       .catch((error) => {
        console.log(error);
      });
  
    },
    resetVisit(){
      this.selectedSlots=[]
      this.schedule_id="",
      this.cleaning_date="",
       this.cleaning_time="",
       this.cleaning_hours="",
       this.no_of_cleaners="",
       this.selected_no_of_cleaners="",
       this.selectedSlots=[]
      this.setDate(moment().format('MM/DD/YYYY'))
    this.selected_date=moment().format('DD-MM-YYYY')
    $('#date_hidden').val(moment().format('MM/DD/YYYY'))
    },
    
   
    addVisit(){
      if(this.selectedSlots.length<1){
        this.visit_err='Please select atleast one slot'
      }
      else if(!this.selected_no_of_cleaners){
        this.visit_err='Please select the number of cleaners'
      }
      else{

        var start_date=Object.keys(this.selected_slots)[0]
        var minhour=Math.min(...this.selected_slots[start_date])
      axios.post(this.url+'/customer/editorder/'+this.orderId,{
        action_type:'add_cleaning',
        evaluation_book_id:this.evaluation_book_id,
        cleaning_date:start_date,
        cleaning_time:this.slotFormat[minhour].start_time,
        cleaning_hours:this.countSelection()*2,
       no_of_cleaners:parseInt(this.selected_no_of_cleaners)
      }).then(response=>{
        $('#visit-close').click()
        location.reload()
       
      })
    }
    },
    saveCustomerNote(){
      axios.post(this.url+'/customer/editorder/'+this.orderId,{
        action_type:'evaluator_note',
        evaluator_note:this.customer_note

      }).then(response=>{
        $('#close_customer_note').click()
        location.reload()
      })
    },
    
    uploadImage(){

      for(var i=0;i<this.media_files.length;i++){
        this.imageForm.append('media',this.media_files[i])
      }
      this.imageForm.append('action_type','evaluation_media')
      this.imageForm.append('evaluationbook_id',this.image_eval_id)
      this.imageForm.append('taken_status',this.taken_status)
    
      axios.post(this.url+'/customer/editorder/'+this.orderId,this.imageForm).then(response=>{
       window.location.reload()
       this.imageForm=new FormData()
      }).catch(err=>{
        this.imageForm=new FormData()
      })
    },
   
    deleteVisit(){
      axios.post(this.url+'/customer/editorder/'+this.orderId,{
        action_type:'cancell_cleaning',
        evaluation_book_id:this.evaluation_book_id,
        schedule_id:this.schedule_id,
        reduction_status:false,
       
        
      }).then(response=>{
       
        location.reload()
       
      })
    },
    cancelVisit(){
     
      if(this.reduction_status){
        var post_data={
          action_type:'cancell_cleaning',
        evaluation_book_id:this.evaluation_book_id,
        schedule_id:this.schedule_id,
        reduction_status:this.reduction_status,
        reduction_amount:this.reducing_total,  
        }
      }
      else{
        var post_data={
          action_type:'cancell_cleaning',
        evaluation_book_id:this.evaluation_book_id,
        schedule_id:this.schedule_id,
        reduction_status:this.reduction_status,
        }
      }
      axios.post(this.url+'/customer/editorder/'+this.orderId,post_data).then(response=>{
        
        location.reload()
       
      })
    },
    editVisit(){
      if(this.countSelection()<1){
        this.visit_err='Please select atleast one slot'
      }
      else if(!this.selected_no_of_cleaners){
        this.visit_err='Please select the number of cleaners'
      }
      else{
      var start_date=Object.keys(this.selected_slots)[0]
      
      var minhour=Math.min(...this.selected_slots[start_date])
      axios.post(this.url+'/customer/editorder/'+this.orderId,{
        action_type:'edit_cleaning',
        evaluation_book_id:this.evaluation_book_id,
        schedule_id:this.schedule_id,
        cleaning_date:start_date,
       cleaning_time:this.slotFormat[minhour].start_time,
       cleaning_hours:this.countSelection()*2,
       no_of_cleaners:parseInt(this.selected_no_of_cleaners)
      }).then(response=>{
        
        location.reload()
       
      })
    }
    },
    /*getOtherKeynotes(keynotes){
      var otherKeynotes
      for(var i=0;i<keynotes;i++){

      }
      if(keynote.sub_area=='kitchen')
    },*/
    getTheKitchens(){
      this.kitchen_keynotes=[]
      var kitchens=[]
      console.log("val is"+JSON.stringify(this.editSectionData))
      for(var i=0;i<this.editSectionData.keynotes.length;i++){
        if(this.editSectionData.keynotes[i].sub_area=='kitchen'){
          var keynote={
            sub_area:this.editSectionData.keynotes[i].sub_area,
            quantity:JSON.parse(this.editSectionData.keynotes[i].quantity)
          }
          if(keynote.quantity.type=='new'){
            for(var sz=0;sz<this.new_kitchen_size.length;sz++){
              if(this.new_kitchen_size[sz].name==keynote.quantity.size){
                keynote.quantity.size=this.new_kitchen_size[sz]
              }
            }
          }
          else if(keynote.quantity.type=='old'){
            for(var sz=0;sz<this.old_kitchen_size.length;sz++){
              if(this.old_kitchen_size[sz].name==keynote.quantity.size){
                keynote.quantity.size=this.old_kitchen_size[sz]
              }
            }
          }
          kitchens.push(keynote)
        }
       
      }
      console.log("quantity is"+JSON.stringify(kitchens))
      this.kitchen_keynotes=kitchens
      
    },
    getOtherKeynotes(){
      var others=[]
      this.other_keynotes=[]
      console.log("val is"+JSON.stringify(this.editSectionData))
      for(var i=0;i<this.editSectionData.keynotes.length;i++){
        if(this.editSectionData.keynotes[i].sub_area!='kitchen'){
          var keynote={
            sub_area:this.editSectionData.keynotes[i].sub_area,
            quantity:this.editSectionData.keynotes[i].quantity
          }
          others.push(keynote)
        }
       
      }
     
      this.other_keynotes= others
    },
    calDiscount(){
      this.paymentData.final_amount=parseFloat(this.total_amount)-(parseFloat(this.paymentData.discount)||0)+(parseFloat(this.paymentData.additional_charge)||0)-(parseFloat(this.cancelledAmount)||0)
      this.paymentData.amount_after_cleaning=''
      this.paymentData.amount_before_cleaning=''
    },
    // calAdditionalCharge(){
     
    //   this.paymentData.final_amount=parseFloat(this.total_amount)+parseFloat(this.paymentData.additional_charge)||0
    //   this.paymentData.amount_after_cleaning=''
    //   this.paymentData.amount_before_cleaning=''
    // },
    calcBreakdownBefore(){
      this.paymentData.amount_after_cleaning=this.paymentData.final_amount-this.paymentData.amount_before_cleaning
    },
    calcBreakdownAfter(){
      this.paymentData.amount_before_cleaning=this.paymentData.final_amount-this.paymentData.amount_after_cleaning
    },
    openPayment(){
      $('#edit-payment-tigger').click()
    },
    editSection(index,sid,service){
      this.action_type="Edit"
      this.service_type=$(service).data('service')
      console.log("index is"+index)
     // var sectiondata=$(section).data()
      
     this.editSectionData.section_id=sid
      console.log("section is "+JSON.stringify(this.sections[index-1]))
      this.sectionData=this.sections[index-1]
      if(this.service_type=='Facade Cleaning'){
        this.editSectionData.is_highprice_facade=this.sections[index-1].is_highprice_facade
        
      }
      $('#edit-dialog-tigger').click()
      this.editSectionData.section_cost=this.sectionData.section_cost
      this.editSectionData.section_net_cost=this.sectionData.section_net_cost
      this.editSectionData.sectiononly_cost=this.sectionData.sectiononly_cost
      this.editSectionData.sectiononly_net_cost=this.sectionData.sectiononly_net_cost
      this.editSectionData.section_name=this.sectionData.section_name
      
      
    },
    recalcAddonCost(){
      if(this.service_type!='Hourly Cleaning')
      {
      this.priceupdate=false
      var addon_cost=0
      for(var i=0;i<this.kitchen_addons.length;i++){
        if(this.service_type!='General Cleaning')
        {
             addon_cost=addon_cost+ this.kitchen_addons[i].addon_net_cost
        }
        else{
          if(this.kitchen_addons[i].other_details.type=='old'){
            addon_cost=addon_cost+ this.kitchen_addons[i].addon_net_cost
          }
        }
      }
      var sectiononlycost=this.editSectionData.sectiononly_cost||0
      this.editSectionData.section_cost=sectiononlycost+addon_cost
      
      this.priceupdate=true
    }
    },
    deleteSection(index,sid){
     
      console.log("index is"+index)
     // var sectiondata=$(section).data()
     this.deleteSectionData.section_id=sid
     /* console.log("section is "+JSON.stringify(this.sections[index-1]))
      this.sectionData=this.sections[index-1]*/
      $('#delete-section-tigger').click()
     
      
    },
    deleteTheSection(){
      axios.post(this.url+'/customer/editorder/'+this.orderId,{
        action_type:'delete_section',
        section_id:this.deleteSectionData.section_id
      }).then(response=>{
        console.log(response)
        location.reload();
      })
    },
    resetKitchenAddonSize(index){
      this.kitchen_addons[index].size={}
      this.kitchen_addons[index].addon_cost=0
      this.kitchen_addons[index].addon_net_cost=0
      this.recalcAddonCost()
    },

    
    changeCategory(){
      this.service_productivity=[]
     // this.editSectionData.size={}
      if(this.editSectionData.category=='Kitchen'){
        var service='Kitchen Cleaning'
        axios.get(this.url+'/customer/ajax/getservicesizeprice?service_type='+service).then(response=>{
          this.productivity=response.data
          for(var i in this.productivity){
            if(!this.editSectionData.is_newkitchen && !this.productivity[i].is_newkitchen){
              this.service_productivity.push(this.productivity[i])
            }
            else if(this.editSectionData.is_newkitchen && this.productivity[i].is_newkitchen){
              this.service_productivity.push(this.productivity[i])
            }
           
          }
      })
      }
      else {
        this.getProductivity()
      }
    },
    updateNotes(){
      axios.post(this.url+'/customer/editorder/'+this.orderId,{
        "action_type":'evaluationbook_note',
       "evaluationbook_id":this.eval_book_id,
       "note":this.notes,
       
       
      }).then(response=>{
        console.log(response)
        $('#note-close').click()
        window.location.reload()
        
      })
    },
    updateDiscount(){
      if(this.paymentData.payment_method=='BREAKDOWN')
      {
       
      axios.post(this.url+'/customer/editorder/'+this.orderId,{
        "action_type":'edit_discount',
       "payment_method":this.paymentData.payment_method,
       "discount_amount":parseInt(this.paymentData.discount)||0,
       "before_cleaning_amount":parseInt(this.paymentData.amount_before_cleaning),
       "after_cleaning_amount":parseInt(this.paymentData.amount_after_cleaning),
       "additional_charge":parseFloat(this.paymentData.additional_charge)||0,
      }).then(response=>{
        console.log(response)
        $('#edit-payment-close').click()
       window.location.reload()
        
      })
    }
      else
      {
      axios.post(this.url+'/customer/editorder/'+this.orderId,{
        "action_type":'edit_discount',
       "payment_method":this.paymentData.payment_method,
       "discount_amount":parseInt(this.paymentData.discount)||0,
       "additional_charge":parseFloat(this.paymentData.additional_charge)||0,
       
      }).then(response=>{
        console.log(response)
        $('#edit-payment-close').click()
        window.location.reload()
      })
      }
      
    },
    updateEvaluation(){
      if(this.paymentData.payment_method=='BREAKDOWN')
      {
       
      axios.post(this.url+'/customer/editorder/'+this.orderId,{
        "action_type":'submit_quatation',
       "payment_method":this.paymentData.payment_method,
       "discount_amount":parseInt(this.paymentData.discount)||0,
       "additional_charge":parseFloat(this.paymentData.additional_charge)||0,
       "before_cleaning_amount":parseInt(this.paymentData.amount_before_cleaning),
       "after_cleaning_amount":parseInt(this.paymentData.amount_after_cleaning),
       
      }).then(response=>{
        console.log(response)
        $('#submit-close').click()
        window.location.reload()
        
      })
    }
      else
      {
      axios.post(this.url+'/customer/editorder/'+this.orderId,{
        "action_type":'submit_quatation',
       "payment_method":this.paymentData.payment_method,
       "discount_amount":parseInt(this.paymentData.discount)||0,
       "additional_charge":parseFloat(this.paymentData.additional_charge)||0
       
       
      }).then(response=>{
        console.log(response)
        $('#submit-close').click()
        window.location.reload()
      })
      }
      
    },
    parseKeynotes(){
      this.final_keynotes=[]
      for(var i=0;i<this.kitchen_keynotes.length;i++){
        this.final_keynotes.push({
          sub_area:'kitchen',
          quantity:JSON.stringify({
            cost:this.kitchen_keynotes[i].quantity.size.cost,
            max_size:this.kitchen_keynotes[i].quantity.size.max_size,
            residue:this.kitchen_keynotes[i].quantity.residue,
            type:this.kitchen_keynotes[i].quantity.type,
            size:this.kitchen_keynotes[i].quantity.size.name
          })
        })
      }
      for(var i=0;i<this.other_keynotes.length;i++){
        this.final_keynotes.push({
          sub_area:this.other_keynotes[i].sub_area,
          quantity:this.other_keynotes[i].quantity
        })
      }

    },
    resetKitchenSize(){
      this.editSectionData.size={}
      this.calcSectionCost()
    },
    resetWindowSize(){
      this.editSectionData.size={}
      this.calcSectionCost()
      
    },
    resetFacadeSize(){
      this.editSectionData.size={}
    },
    updateSection(){
      this.parseKeynotes()
      var sectionData={}
      console.log("section net cost is"+this.editSectionData.section_net_cost)
      sectionData=
        {
          "section_name":this.editSectionData.section_name,
          "size":this.editSectionData.size.name,
          "wall_type":"",
          "ceiling_type":"",
          "floor_type":"",
          "cement_residue":false,
          "section_cost":this.editSectionData.section_cost,
          "sectiononly_cost":this.editSectionData.sectiononly_cost,
          "sectiononly_net_cost":this.editSectionData.sectiononly_net_cost,

          "section_net_cost":this.editSectionData.section_cost,
          "new_kitchen":this.editSectionData.new_kitchen,
          "oil_residue":this.editSectionData.oil_residue,
          "is_cabinet":this.editSectionData.is_cabinet,
         "is_highprice_facade":false,
         "is_highprice_window":false,
      }
      if(this.service_type=='Window Cleaning'){
      
          sectionData.is_highprice_window=this.editSectionData.is_highprice_window
        
      }
      if(this.service_type=='Upholstery Cleaning'){
        if(!this.editSectionData.size.name){
          sectionData.size=this.editSectionData.size+" Seater"
        }
      }
      
      if(this.editSectionData.wall_type.length>0){
        sectionData.wall_type=this.editSectionData.wall_type.join() 
        console.log("in wall type : "+this.editSectionData.wall_type)  
      }
      if(this.editSectionData.floor_type.length>0){
        sectionData.floor_type=this.editSectionData.floor_type.join()   
      }
      if(this.editSectionData.ceiling_type.length>0){
        sectionData.ceiling_type=this.editSectionData.ceiling_type.join()   
      }
      if(this.editSectionData.material){
        if(this.editSectionData.material.length>0){
          sectionData.material=this.editSectionData.material.join()   
        }
      }
      if(this.editSectionData.cause_of_stain){
      if(this.editSectionData.cause_of_stain.length>0){
        sectionData.cause_of_stain=this.editSectionData.cause_of_stain.join()   
      }
    }
    
      if(this.editSectionData.age_of_stain){
        sectionData.age_of_stain=this.editSectionData.age_of_stain   
      }
    
    if(this.editSectionData.colour){
      if(this.editSectionData.colour.length>0){
        sectionData.colour=this.editSectionData.colour.join()   
      }
    }
    if(this.service_type=='General Cleaning'||this.service_type=='Deep Cleaning'||this.service_type=='Hourly Cleaning'){
      for(var i=0;i<this.kitchen_addons.length;i++){
        this.kitchen_addons[i].quantity=parseInt(this.kitchen_addons[i].quantity)
        this.kitchen_addons[i].other_details.size=this.kitchen_addons[i].other_details.size.name
        this.kitchen_addons[i].other_details=JSON.stringify(this.kitchen_addons[i].other_details)
      }
    }
    console.log("section net cost before sending is"+this.editSectionData.section_net_cost)
      axios.post(this.url+'/customer/editorder/'+this.orderId,{
        "action_type":'edit_section',
        "evaluation_book__id":this.eval_book_id,
        "section_details":sectionData,
        "keynotes":this.final_keynotes,
        "addons":this.kitchen_addons,
        "section_id":this.editSectionData.section_id,
      }).then(response=>{
        console.log(response)
        $('#edit-section-close').click()
       this.resetSection()
        location.reload()
      })
    },
    addSectionData(){
      var sectionData={}
     // this.other_keynotes=[]
     // this.kitchen_keynotes=[]
     this.parseKeynotes()
      sectionData=
        {
          "section_name":this.editSectionData.section_name,
          "size":this.editSectionData.size.name,
          "wall_type":"",
          "ceiling_type":"",
          "floor_type":"",
          "cement_residue":false,
          "section_cost":this.editSectionData.section_cost,
          "section_net_cost":this.editSectionData.section_cost,
          "sectiononly_cost":this.editSectionData.sectiononly_cost,
          "sectiononly_net_cost":this.editSectionData.sectiononly_net_cost,
          "new_kitchen":this.editSectionData.is_newkitchen,
         "is_highprice_facade":false,
         "is_highprice_window":false,
      }
      if(this.service_type=='Window Cleaning'){
      
        sectionData.is_highprice_window=this.editSectionData.is_highprice_window
      
    }
      if(this.editSectionData.wall_type.length>0){
        sectionData.wall_type=this.editSectionData.wall_type.join()   
      }
      if(this.editSectionData.floor_type.length>0){
        sectionData.floor_type=this.editSectionData.floor_type.join()   
      }
      if(this.editSectionData.ceiling_type.length>0){
        sectionData.ceiling_type=this.editSectionData.ceiling_type.join()   
      }
      if(this.service_type=='General Cleaning'||this.service_type=='Deep Cleaning'||this.service_type=='Hourly Cleaning'){
        for(var i=0;i<this.kitchen_addons.length;i++){
          this.kitchen_addons[i].quantity=parseInt(this.kitchen_addons[i].quantity)
          this.kitchen_addons[i].other_details.size=this.kitchen_addons[i].other_details.size.name
          this.kitchen_addons[i].other_details=JSON.stringify(this.kitchen_addons[i].other_details)
        }
      }
      axios.post(this.url+'/customer/editorder/'+this.orderId,{
        "action_type":'add_section',
        "evaluation_book__id":this.eval_book_id,
        "section_details":sectionData,
        "keynotes":this.final_keynotes,
        "addons":this.kitchen_addons
       
      }).then(response=>{
        console.log(response)
        $('#edit-section-close').click()
        this.resetSection()
      })
    },
    
    resetSection(){
      this.productivity={},
      this.service_productivity=[],
             this.editSectionData={
              size:{},
              area_type:[],
              section_cost:0,
              section_net_cost:0,
              section_name:'',
              floor_type:[],
              ceiling_type:[],
              floor_type:[],
              material:[],
              category:'Floor',
              age:null,
              is_cabinet:false,
              newkitchen:false
             },
             this.section_cost=0
             this.final_keynotes=[]
             this.other_keynotes=[]
             this.kitchen_keynotes=[]
              location.reload()   
    },
    getOrderId(){
      var orderId=window.location.href.split('/')[7]
      this.orderId=orderId
      console.log("orderid is"+orderId)

     
    },
    getSections(id){
      console.log("sectionid is"+id)
      console.log("data is"+JSON.stringify(this.sections[id]))
      
      this.currentSection=this.sections[id]
      this.gotSection=true
      return this.currentSection
    },
    calcSofaSize(){
     var found =false
     var sofa={}
      for(var i=0;i<this.sofa_size.length;i++){
        if(this.editSectionData.size<=this.sofa_size[i].max_size){
          found=true
          sofa=this.sofa_size[i]
          break;
        }
      }
      if(found){
        this.editSectionData.section_cost=sofa.cost
      }
      if(!found){
         // var temp = this.sofa_size[this.sofa_size.length-1].cost
          //var rem=parseInt(this.editSectionData.size)-this.sofa_size[this.sofa_size.length-1].max_size
         // this.editSectionData.section_cost=temp+(rem*this.sofa_size[0].unit_price)
         this.editSectionData.section_cost=this.editSectionData.size*this.sofa_size[0].unit_price
      }
      
    },
     getSection(id){
      this.eval_book_id=id
     this.new_count=this.visit_count
        axios.get(this.url+'/customer/editorder/'+this.orderId+'?evaluation_book_id='+id).then(response=>{
          this.sections=response.data.section_details.evaluationsection_book
          this.service_type=response.data.section_details.service_type.name
          
           this.service_size=[]
           this.chair_size=[]
           this.sofa_size=[]
           var serv=this.service_type
           if(serv=='Hourly Cleaning'){
             serv='General Cleaning'
           }
           axios.get(this.url+'/customer/ajax/getservicesizeprice?service_type='+serv).then(response=>{
            var size=response.data
            for(var i in size){
              this.service_size.push(size[i])
              size[i].combined_size=size[i].name+' ( '+size[i].min_size+' sq.m - '+size[i].max_size+' sq.m )'
              if(size[i].upholstery_type=='CHAIR'){
                

                this.chair_size.push(size[i])
              }
              else if(size[i].upholstery_type=='SOFA')
              {
                this.sofa_size.push(size[i])
              }
            }
            console.log("size is"+JSON.stringify(this.service_size))
          /* old order size conversion */
              

          /* new order size conversion begins here */
        
           /* General cleaning  size conversion */ 
          if(this.service_type=='General Cleaning' || this.service_type=='Deep Cleaning' || this.service_type=='Storage Area' || this.service_type=='Sterilization'|| this.service_type=='Carpet Cleaning'|| this.service_type=='Car Parking Umbrella' || this.service_type=='Outdoor Cleaning' || this.service_type=='Hourly Cleaning'){
            for(var j=0;j<this.sections.length;j++){
             
              for(var i=0;i<this.service_size.length;i++){
                if(parseInt(this.sections[j].size)){
                  var section_size=parseInt(this.sections[j].size)
                  if(section_size<=this.service_size[i].max_size && section_size>=this.service_size[i].min_size){
                    this.sections[j].size=this.service_size[i]
                   
                  }
                }
                else{
                  if(this.service_size[i].name==this.sections[j].size){
                    this.sections[j].size=this.service_size[i]
                   
                  }
                }
                
              }
            }
              
          }
          /* Upholstery cleaning  size conversion */ 
          if(this.service_type=='Upholstery Cleaning'){
           var type=""
            for(var j=0;j<this.sections.length;j++){
              if(this.sections[j].size.includes('Seater')||this.sections[j].upholstery_type=='SOFA'){
                type="SOFA"
                //this.sections[j].size=this.this.sections[j].size.split(" ")[0]
                if(this.sections[j].upholstery_type=='SOFA' && !this.sections[j].size.includes('Seater')){
                  for(var i=0;i<this.service_size.length;i++){
                    if(this.service_size[i].upholstery_type=="SOFA" && this.sections[j].size==this.service_size[i].name){
                      
                      this.sections[j].size=this.service_size[i].max_size

                     
                    }
                  }
                
                }
                else{
                  this.sections[j].size=this.sections[j].size.split(" ")[0]
                  console.log("section size is "+this.sections[j].size.split(" ")[0])
                }
                
               
                this.sections[j].upholstery_type="SOFA"
              }
              else{
                type="CHAIR"
                this.sections[j].upholstery_type="CHAIR"
              }
              console.log("type is"+type)
              if(type=="CHAIR"){
                for(var i=0;i<this.service_size.length;i++){
                  if(this.service_size[i].upholstery_type=="CHAIR" && this.sections[j].size==this.service_size[i].name){
                    
                    this.sections[j].size=this.service_size[i]
                   
                  }
                }
              }
             
            }
              
          } 
         /* kitchen cleaning */
         if(this.service_type=='Kitchen Cleaning'){
        
           for(var j=0;j<this.sections.length;j++){
            
             
            
             if(this.sections[j].new_kitchen){
               for(var i=0;i<this.service_size.length;i++){
                if(parseInt(this.sections[j].size)){
                  var section_size=parseInt(this.sections[j].size)
                  if(section_size<=this.service_size[i].max_size && section_size>=this.service_size[i].min_size && this.service_size[i].is_newkitchen){
                    this.sections[j].size=this.service_size[i]
                   
                  }
                }
                else{
                 if(this.service_size[i].is_newkitchen && this.sections[j].size==this.service_size[i].name){
                   
                   this.sections[j].size=this.service_size[i]
                  
                 }
                }
               }
             }
             else{
              for(var i=0;i<this.service_size.length;i++){
                if(parseInt(this.sections[j].size)){
                  var section_size=parseInt(this.sections[j].size)
                  if(section_size<=this.service_size[i].max_size && section_size>=this.service_size[i].min_size && !this.service_size[i].is_newkitchen){
                    this.sections[j].size=this.service_size[i]
                   
                  }
                }
                else{
                if(!this.service_size[i].is_newkitchen && this.sections[j].size==this.service_size[i].name){
                  
                  this.sections[j].size=this.service_size[i]
                 
                }
              }
            }
             }
            
           }
             
         }
         
         /** Facade Cleaning */
         if(this.service_type=='Facade Cleaning'){
           this.highprice_facade=[]
           this.lowprice_facade=[]
          for(var i=0;i<this.service_size.length;i++){
            
            if(this.service_size[i].is_highprice_facade){
              this.service_size[i].combined_size=this.service_size[i].name+' ( '+this.service_size[i].min_size+' sq.m - '+this.service_size[i].max_size+' sq.m )'
              this.highprice_facade.push(this.service_size[i])
            }
            else{
              this.service_size[i].combined_size=this.service_size[i].name+' ( '+this.service_size[i].min_size+' sq.m - '+this.service_size[i].max_size+' sq.m )'
              this.lowprice_facade.push(this.service_size[i])
            }
            
          }
        
          for(var j=0;j<this.sections.length;j++){
           
            
           
            if(this.sections[j].is_highprice_facade){
             
              for(var i=0;i<this.service_size.length;i++){
                if(this.service_size[i].is_highprice_facade && this.sections[j].size==this.service_size[i].name){
                  
                  this.sections[j].size=this.service_size[i]
                 
                }
                
                
              }
            }
            else{
             for(var i=0;i<this.service_size.length;i++){
               if(!this.service_size[i].is_highprice_facade && this.sections[j].size==this.service_size[i].name){
                 
                 this.sections[j].size=this.service_size[i]
                
               }
               
             }
            }
           
          }
            
        }
        /** window cleaning */
        if(this.service_type=='Window Cleaning'){
        
          for(var j=0;j<this.sections.length;j++){
            this.highprice_window=[]
            this.lowprice_window=[]
            
           
            if(this.sections[j].is_highprice_window){
              for(var i=0;i<this.service_size.length;i++){
                if(this.service_size[i].is_highprice_window && this.sections[j].size==this.service_size[i].name){
                  
                  this.sections[j].size=this.service_size[i]
                 
                }
                if(this.service_size[i].is_highprice_window){
                  this.service_size[i].combined_size=this.service_size[i].name+' ( '+this.service_size[i].min_size+' sq.m - '+this.service_size[i].max_size+' sq.m )'
                  this.highprice_window.push(this.service_size[i])
                }
                else{
                  this.service_size[i].combined_size=this.service_size[i].name+' ( '+this.service_size[i].min_size+' sq.m - '+this.service_size[i].max_size+' sq.m )'
                  this.lowprice_window.push(this.service_size[i])
                }
              }
            }
            else{
             for(var i=0;i<this.service_size.length;i++){
               if(!this.service_size[i].is_highprice_window && this.sections[j].size==this.service_size[i].name){
                 
                 this.sections[j].size=this.service_size[i]
                
               }
             }
            }
           
          }
            
        }
        })
          
        }).catch(err=>{
          console.log(err)
        })
    },
    onChange(event) {
      if(event.target.value == "BREAKDOWN"){
        this.breakDownFlag= true
      }else{
        this.breakDownFlag =false
      }
      console.log(this.amount)
  },
  calcSectionCost(){
    if(this.service_type!='Hourly Cleaning')
    {
    this.priceupdate=false
    this.editSectionData.sectiononly_cost=this.editSectionData.size.cost||0
    this.editSectionData.sectiononly_net_cost=this.editSectionData.size.cost||0
    this.fixed_section_cost=this.editSectionData.section_cost
    this.recalcKeynoteCost()
    this.recalcAddonCost()
    this.priceupdate=true
    }
  },
    setDate(d){
    
      this.soltdate =  new Date(d)
      var todaysDate = new Date(d)
      todaysDate = new Date(d).toDateString().split(" ");
      this.year = todaysDate[3]
      this.day = todaysDate[0]+", "+todaysDate[1]+" "+todaysDate[2]
    },
    resetContacts(){
      this.contacts=[]
    },
    getProductivity(){
      this.service_productivity=[]
      var serv=this.service_type
      if(serv=='Hourly Cleaning'){
        serv='General Cleaning'
      }
      axios.get(this.url+'/customer/ajax/getservicesizeprice?service_type='+serv).then(response=>{
          this.productivity=response.data
          for(var i in this.productivity){
            this.productivity[i].combined_size=this.productivity[i].name+' ( '+this.productivity[i].min_size+' sq.m - '+this.productivity[i].max_size+' sq.m )'

            this.service_productivity.push(this.productivity[i])
          }
          if(this.service_type=='Kitchen Cleaning'){
            this.formatKitchenSize()
          }
         
      })
    },
    async getServiceSize(){
        var serv=this.service_type
        if(serv=='Hourly Cleaning'){
          serv='General Cleaning'
        }
      this.service_size=[]
      await axios.get(this.url+'/customer/ajax/getservicesizeprice?service_type='+serv).then(response=>{
          var size=response.data
          for(var i in size){
            this.service_size.push(size[i])
          }
         
         
         
      }
      )
      return this.service_size
    },
    parseUpholstery(){
      if(this.editSectionData){}
    }
  }
 
});

