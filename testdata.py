{
"service_types":["General Cleaning"],
"cleaning_datetime_start":"13-06-2021 12:00 pm",
"cleaning_datetime_end":"13-06-2021 03:00 pm"
}

{
"action_type": "edit_cleaning_withautofix",
"cleaning_end": "29-05-2021 09:00 AM",
"cleaning_hours": 9,
"cleaning_start": "29-05-2021 12:00 AM",
"evaluation_id": "BLC20210410067",
"no_of_cleaners": 3,
"schedules": [782],
"service_types": ["General Cleaning"]
}


{
"number_of_cleaners":4,
"cleaning_hours":3,
"service_types":["General Cleaning"],
"cleaning_datetimes":["01-05-2021 12:00 pm","01-05-2021 03:00 pm"]
}



#Evaluation Booking
#
Get
"booking_date":"01-01-2023",
"booking_time":"08:00 AM"

##
{
"booking_date":"01-01-2023",
"booking_time":"08:00 AM"
}

###
{
   "evaluation_id":261,
   "booking_id":82,
   "customer_id":53,
   "customer_details":{
      "name":"Ansab mabu",
      "gender":"MALE",
      "email":"ansabm2015@gmail.com",
      "mobile_number":"89786745",
      "date_day":5,
      "date_month":7,
      "date_year":2018,
      "nationality":"KW",
      "sms_preference":"ENGLISH",
      "contact_platform":"SMS,Email"
   },
   "address_id":27,
   "address_details":{
      "governorate":1,
      "area":1,
      "block":7,
      "avenue":"avenue",
      "building":"ABC",
      "street":"bekhinnham",
      "floor":4,
      "apartment":"ALDHAR"
   }
}


####
GET
   "booking_id":81,
   "evaluationdetails_id":261  

##multiple service save

{
   "service_details":{
      "1":{
         "service_type":1,
         "location_type":"GYM",
         "cleaning_policy":"ONE TIME SERVICE",
         "area_type":"Post Construction",
         "evaluator_note":"test addition of service",
         "is_newkitchen":False,
         "is_highprice_facade":False,
         "is_highprice_window":False,
         "upholstery_type":"CHAIR",
         "estimated_cost":150,
         "total_cost":150,
         "number_of_cleaners":5,
         "cleaning_hours":4,
         "sections":{
            "1":{
               "section_name":"Building1Floor1Apartment1",
               "size":"small",
               "wall_type":"wooden,concrete",
               "ceiling_type":"wooden,ceramic",
               "cement_residue":false,
               "section_cost":100,
               "section_net_cost":100,
               "keynotes":{
                  "1":{
                     "sub_area":"bathroom",
                     "quantity":5
                  },
                  "2":{
                     "sub_area":"bedroom",
                     "quantity":4
                  }
               }
            },
            "2":{
               "section_name":"Building1Floor1Apartment2",
               "size":"medium",
               "wall_type":"wooden,concrete",
               "ceiling_type":"wooden,ceramic",
               "cement_residue":true,
               "section_cost":50,
               "section_net_cost":50,
               "keynotes":{
                  "1":{
                     "sub_area":"windows",
                     "quantity":3
                  },
                  "2":{
                     "sub_area":"bedroom",
                     "quantity":4
                  }
               }
            }
         }
      },
      "2":{
         "service_type":2,
         "location_type":"GYM",
         "cleaning_policy":"ONE TIME SERVICE",
         "area_type":"Post Construction",
         "evaluator_note":"test addition of service",
         "estimated_cost":150,
         "total_cost":150,
         "number_of_cleaners":5,
         "cleaning_hours":4,
         "sections":{
            "1":{
               "section_name":"Building1Floor1Apartment1",
               "size":"small",
               "wall_type":"wooden,concrete",
               "ceiling_type":"wooden,ceramic",
               "cement_residue":false,
               "section_cost":100,
               "section_net_cost":100,
               "keynotes":{
                  "1":{
                     "sub_area":"bathroom",
                     "quantity":5
                  },
                  "2":{
                     "sub_area":"bedroom",
                     "quantity":4
                  }
               }
            },
            "2":{
               "section_name":"Building1Floor1Apartment2",
               "size":"medium",
               "wall_type":"wooden,concrete",
               "ceiling_type":"wooden,ceramic",
               "cement_residue":true,
               "section_cost":50,
               "section_net_cost":50,
               "keynotes":{
                  "1":{
                     "sub_area":"windows",
                     "quantity":3
                  },
                  "2":{
                     "sub_area":"bedroom",
                     "quantity":4
                  }
               }
            }
         }
      }
   },
   "customer_id":53,
   "customer_details":{
      "name":"Ansab mabu",
      "gender":"MALE",
      "email":"ansabm2015@gmail.com",
      "mobile_number":"89786745",
      "date_day":5,
      "date_month":7,
      "date_year":2018,
      "nationality":"KW",
      "sms_preference":"ENGLISH",
      "contact_platform":"SMS,Email"
   },
   "address_id":64,
   "address_details":{
      "governorate":1,
      "area":1,
      "block":7,
      "avenue":"avenue",
      "building":"ABC",
      "street":"bekhinnham",
      "floor":4,
      "apartment":"ALDHAR"
   },
   "schedule_details":{
      "1":{
         "date":"02-06-2022",
         "time":"08:00 pm",
         "no_of_cleaners":7,
         "cleaning_hours":3
      }
   },
   "total_cost":500,
   "estimated_cost":500
}



#multiple service with booking id
{
   "booking_id":210410012,
   "service_details":{
      "1":{
         "service_type":2,
         "location_type":"GYM",
         "area_type":"Post Construction",
         "evaluator_note":"test addition of service",
         
         "upholstery_type":"CHAIR",
         "estimated_cost":150,
         "total_cost":150,
         "number_of_cleaners":5,
         "cleaning_hours":4,
         "sections":{
            "1":{
               "section_name":"Building1Floor1Apartment1",
               "size":"small",
               "wall_type":"wooden,concrete",
               "ceiling_type":"wooden,ceramic",
               "cement_residue":false,
               "section_cost":100,
               "section_net_cost":100,
               "is_newkitchen":False,
              "is_highprice_facade":False,
              "is_highprice_window":False,
               "keynotes":{
                  "1":{
                     "sub_area":"bathroom",
                     "quantity":5
                  },
                  "2":{
                     "sub_area":"bedroom",
                     "quantity":4
                  }
               }
            },
            "2":{
               "section_name":"Building1Floor1Apartment2",
               "size":"medium",
               "wall_type":"wooden,concrete",
               "ceiling_type":"wooden,ceramic",
               "cement_residue":true,
               "section_cost":50,
               "section_net_cost":50,
               "is_newkitchen":False,
              "is_highprice_facade":False,
              "is_highprice_window":False,
               "keynotes":{
                  "1":{
                     "sub_area":"windows",
                     "quantity":3
                  },
                  "2":{
                     "sub_area":"bedroom",
                     "quantity":4
                  }
               }
            }
         }
      }
      
   },
   "customer_id":53,
   "customer_details":{
      "name":"Ansab mabu",
      "gender":"MALE",
      "email":"ansabm2015@gmail.com",
      "mobile_number":"89786745",
      "date_day":5,
      "date_month":7,
      "date_year":2018,
      "nationality":"KW",
      "sms_preference":"ENGLISH",
      "contact_platform":"SMS,Email"
   },
   "address_id":64,
   "address_details":{
      "governorate":1,
      "area":1,
      "block":7,
      "avenue":"avenue",
      "building":"ABC",
      "street":"bekhinnham",
      "floor":4,
      "apartment":"ALDHAR"
   },
   "schedule_details":{
      "1":{
         "date":"02-06-2022",
         "time":"08:00 pm",
         "no_of_cleaners":7,
         "cleaning_hours":3
      }
   },
   "total_cost":500,
   "estimated_cost":500
}
#multiple service with booking id
{
   "service_details":{
      "1":{
         "cleaning_policy":'SUBSCRIPTION' || 'ONE TIME SERVICE',
          "schedule_details":{
            "1":{
                  "date":"02-06-2022",
                  "time":"08:00 pm",
                   "no_of_cleaners":7,
                  "cleaning_hours":3
             }
          },
         "service_type":2,
         "location_type":"GYM",
         "area_type":"Post Construction",
         "evaluator_note":"test addition of service",
         
         "upholstery_type":"CHAIR",
         "estimated_cost":150,
         "total_cost":150,
         "number_of_cleaners":5,
         "cleaning_hours":4,
         "sections":{
            "1":{
               "section_name":"Building1Floor1Apartment1",
               "size":"small",
               "wall_type":"wooden,concrete",
               "ceiling_type":"wooden,ceramic",
               "cement_residue":false,
               "section_cost":100,
               "section_net_cost":100,
               "is_newkitchen":False,
              "is_highprice_facade":False,
              "is_highprice_window":False,
               "keynotes":{
                  "1":{
                     "sub_area":"bathroom",
                     "quantity":5
                  },
                  "2":{
                     "sub_area":"bedroom",
                     "quantity":4
                  }
               }
            },
            "2":{
               "section_name":"Building1Floor1Apartment2",
               "size":"medium",
               "wall_type":"wooden,concrete",
               "ceiling_type":"wooden,ceramic",
               "cement_residue":true,
               "section_cost":50,
               "section_net_cost":50,
               "is_newkitchen":False,
              "is_highprice_facade":False,
              "is_highprice_window":False,
               "keynotes":{
                  "1":{
                     "sub_area":"windows",
                     "quantity":3
                  },
                  "2":{
                     "sub_area":"bedroom",
                     "quantity":4
                  }
               }
            }
         }
      }
      
   },
 
  
   "total_cost":500,
   "estimated_cost":500
}
#customer/evaluatorbookingmultiplephase2/together/ {{ id }}/ - together
#customer/evaluatorbookingmultiplephase2/seperate/ {{ id }}/  - individual



#let the customer book
#evaluatorbookingmultiplephase2/customer/
{
   "service_details":{
      "1":{
        
          
         "service_type":2,
         "location_type":"GYM",
         "area_type":"Post Construction",
         "evaluator_note":"test addition of service",
         
         "upholstery_type":"CHAIR",
         "estimated_cost":150,
         "total_cost":150,
        
         "sections":{
            "1":{
               "section_name":"Building1Floor1Apartment1",
               "size":"small",
               "wall_type":"wooden,concrete",
               "ceiling_type":"wooden,ceramic",
               "cement_residue":false,
               "section_cost":100,
               "section_net_cost":100,
               "is_newkitchen":False,
              "is_highprice_facade":False,
              "is_highprice_window":False,
               "keynotes":{
                  "1":{
                     "sub_area":"bathroom",
                     "quantity":5
                  },
                  "2":{
                     "sub_area":"bedroom",
                     "quantity":4
                  }
               }
            },
            "2":{
               "section_name":"Building1Floor1Apartment2",
               "size":"medium",
               "wall_type":"wooden,concrete",
               "ceiling_type":"wooden,ceramic",
               "cement_residue":true,
               "section_cost":50,
               "section_net_cost":50,
               "is_newkitchen":False,
              "is_highprice_facade":False,
              "is_highprice_window":False,
               "keynotes":{
                  "1":{
                     "sub_area":"windows",
                     "quantity":3
                  },
                  "2":{
                     "sub_area":"bedroom",
                     "quantity":4
                  }
               }
            }
         }
      }
      
   },
 
  
   "total_cost":500,
   "estimated_cost":500
}



