var app=new Vue({
    created()
    {
      let uri = window.location.href.split('?');
      if (uri.length == 2)
      {
        let vars = uri[1].split('&');
        let getVars = {};
        let tmp = '';
        vars.forEach(function(v){
          tmp = v.split('=');
          if(tmp.length == 2)
          getVars[tmp[0]] = tmp[1];
        });
       
        this.activeService=getVars.category
        if(getVars.category)
        {
        this.activeService=this.activeService.split('%20')[0]+' '+this.activeService.split('%20')[1]
        }
        else{
            this.activeService='Detailed Cleaning'
        }
        if(getVars.lang=='ar'){
            this.lang=getVars.lang
            this.arabic=true
        }
        else{
            this.lang='en'
            this.arabic=false
        }
       
       console.log('lamguage is '+this.lang)
      }
      else{
          this.activeService='Detailed Cleaning'
      }
    },

    mounted(){
      
    },
  el: '#webapp',
  // define data - initial display text
  delimiters: ['<%', '%>'],
  data: {
      lastElem:1,
      subItemSelected:'',
      differentSlider:'engDifferent',
      testimonialSlider:'engTestimonial',
    activeTab:false,
    selectedTab:'',
    activeItem:'',
    category:'',
    serviceType:'',
    activeService:'',
    lang:'en',
    arabic:false,
    selectedBooking:'Cleaning'
  },
  methods: {
      selectTab(service){
        this.selectedTab=service
      },
      goTo(url){
        window.location.href=url
      },
      changeToArabic(){
        var servicePage=false
        var uri = window.location.href.split('?lang');
         var uri2=window.location.href.split('&lang') 
         if(uri2.length>1){
            uri=uri2
            servicePage=true
         } 
        this.lang="ar"
        if(uri){
        if(uri.length<2 && uri2.length<2){
            if(!servicePage){
                window.location.href=window.location.href+'?lang=ar'
            }
            else{
                window.location.href=window.location.href+'&lang=ar'
            }
            
        }
        else{
            if(uri[1]=='=ar')
            {
            window.location.href=window.location.href
            }
            else{
                if(!servicePage){
                window.location.href=uri[0]+'?lang=ar'
                }
                else{
                    window.location.href=uri[0]+'&lang=ar'
                }
            }
        }
    }
    },
    changeToEnglish(){
        var servicePage=false
        var uri = window.location.href.split('?lang');
         var uri2=window.location.href.split('&lang') 
         if(uri2.length>1){
            uri=uri2
            servicePage=true
         } 
         if(uri){
            this.lang='en'
            if(uri.length<2 && uri2.length<2 ){
                if(!servicePage){
                window.location.href=window.location.href+'?lang=en'
                }
                else{
                    window.location.href=window.location.href+'&lang=en'
                }
            }
            else{
                if(uri[1]=='=en')
                {
                window.location.href=window.location.href
                }
                else{
                    if(!servicePage){
                    window.location.href=uri[0]+'?lang=en'
                    }
                    else{
                        window.location.href=uri[0]+'&lang=en'
                    }
                }
            }
        }
    },
 changeLang(){
     var servicePage=false
    var uri = window.location.href.split('?lang');
     var uri2=window.location.href.split('&lang') 
     if(uri2.length>1){
        uri=uri2
        servicePage=true
     } 
    if(this.arabic){
        
        this.lang="ar"
        if(uri){
        if(uri.length<2 && uri2.length<2){
            if(!servicePage){
                window.location.href=window.location.href+'?lang=ar'
            }
            else{
                window.location.href=window.location.href+'&lang=ar'
            }
            
        }
        else{
            if(uri[1]=='=ar')
            {
            window.location.href=window.location.href
            }
            else{
                if(!servicePage){
                window.location.href=uri[0]+'?lang=ar'
                }
                else{
                    window.location.href=uri[0]+'&lang=ar'
                }
            }
        }
    }
       
    }
    else{
        if(uri){
        this.lang='en'
        if(uri.length<2 && uri2.length<2 ){
            if(!servicePage){
            window.location.href=window.location.href+'?lang=en'
            }
            else{
                window.location.href=window.location.href+'&lang=en'
            }
        }
        else{
            if(uri[1]=='=en')
            {
            window.location.href=window.location.href
            }
            else{
                if(!servicePage){
                window.location.href=uri[0]+'?lang=en'
                }
                else{
                    window.location.href=uri[0]+'&lang=en'
                }
            }
        }
    }
}
   

 },     
selectNav(nav){
  this.activeTab = true;  
  this.activeItem=nav 
  this.category='Detailed Cleaning'
  this.serviceType='General Cleaning'
},
selectCategory(category){
  this.activeTab = true;  
  this.category=category;
  if(this.category=='Detailed Cleaning'){
      this.serviceType='General Cleaning'
  }
  if(this.category=='Special Care'){
    this.serviceType='Upholstery Cleaning'
}
if(this.category=='Kitchen Cleaning'){
    this.serviceType='Kitchen Cleaning'
}
if(this.category=='Infection Control'){
    this.serviceType='Sanitization & Disinfection'
}
},
selectService(service){
  this.activeTab = true;  
  this.serviceType=service
   
},
mouseleave(){
  this.activeTab = false; 
},
selectBooking(type){
  console.log("i run")
this.selectedBooking=type
},
goToBooking(service){
  var url='http://testbook.bleach-kw.com/#/'
  window.location.href=url+"?service="+service
},
goToBookingPage(){
var url='http://testbook.bleach-kw.com/#/'
if(this.selectedBooking=='Evaluation')
{
window.location.href=url+'evaluator'
}
else{
    window.location.href=url
}
},
slideChange(a){

 if(this.activeService=='Detailed Cleaning' && a==3){
      this.activeService='Special Care'
  }
  else if(this.activeService=='Special Care' && a==4){
    this.activeService='Kitchen Cleaning'
  }
  else if(this.activeService=='Kitchen Cleaning' && a==5){
    this.activeService='Infection Control'
  }
  else if(a==4 && this.activeService=='Infection Control'){
    this.activeService='Kitchen Cleaning'
  }
  else if(a==2 && this.activeService=='Infection Control'){
    this.activeService='Detailed Cleaning'
  }
  else if(a==3 && this.activeService=='Kitchen Cleaning'){
    this.activeService='Special Care'
  }
  else if(a==2 && this.activeService=='Special Care'){
    this.activeService='Detailed Cleaning'
  }
  else if(a==1 && this.activeService=='Detailed Cleaning'){
    this.activeService='Infection Control'
  }
  console.log("active service is"+this.activeService +"a:"+a)
},
prevService(){
 
}
}
})