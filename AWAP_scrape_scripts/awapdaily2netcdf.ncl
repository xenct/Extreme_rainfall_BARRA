;  This program reads in all the daily awap files in the 
; directory the program is run in and creates annual netcdf files. 
; The program can act on all yearly directories present or you can choose
; the directory to act on.
; directories that contain ; the daily ascii files from BoM 
; it will create a netcdf file for every yearly 
; directory.  

load "/usr/share/ncarg/lib/ncarg/nclscripts/csm/gsn_code.ncl"  
load "/usr/share/ncarg/lib/ncarg/nclscripts/csm/gsn_csm.ncl"  
load "/usr/share/ncarg/lib/ncarg/nclscripts/csm/contributed.ncl"



begin
 ;you need to set the variable
 ;vprp3pm,vprp9am,tmax,tmin,pre
 vname = "pre"
 
 ;set the year - set to "all" for all subdirectories
 year = "all"
 
 ;check if this directory contains yearly directories
 if (year.eq."all") then
   fils = systemfunc("ls")
 
   filsint = stringtointeger(fils)

   if (any(filsint.gt.1800).AND.any(filsint.lt.2020)) then 
     ydirs = fils
     numdirs = dimsizes(ydirs)
   end if
   
   delete(year)
   delete(fils)
   
 else
   numdirs = 1
 end if
 
 
 
 ;loop over all directories
 do dd = 1,numdirs
 

   ;get the files names
   if (numdirs.eq.1) then
     ;fils = systemfunc("ls "+year+"/*.grid.gz")
     fils = systemfunc("ls "+year+"/*.grid.Z")
   else
     if (.not.ismissing(filsint(dd-1))) then
       fils = systemfunc("ls "+ydirs(dd-1)+"/*.grid.Z") ; editted this line
       year = stringtointeger(ydirs(dd-1))
       if (dimsizes(fils).eq.1.AND.ismissing(fils)) then
         delete(fils)
         continue
       end if
     else
       continue
     end if  
   end if
   
   print((/year/))
   
   
   ;get filename without the .gz
   print(fils(0))
   suffix = get_file_suffix(fils(0),0)
   fname = suffix@fBase
   
   ;open the first file and get the header information
   if (suffix.eq.".gz") then
     system("gunzip "+fils(0))
   end if
   if (suffix.eq.".Z") then
     system("uncompress "+fils(0))
   end if

   
   header = readAsciiHead(fname,6)
   
 ;  print(header)
   
   headchar = stringtochar(header)
   
   ncols = stringtoint(chartostring(headchar(0,6:)))
   nrows = stringtoint(chartostring(headchar(1,6:)))
   LLlon = stringtofloat(chartostring(headchar(2,9:)))
   LLlat = stringtofloat(chartostring(headchar(3,9:)))
   cellsize = stringtofloat(chartostring(headchar(4,9:)))
   missing = stringtofloat(chartostring(headchar(5,12:)))
   
   ;ncols = str_get_field(header(0),2," ")
   ;nrows = str_get_field(header(1),2," ")
   ;LLlon = str_get_field(header(2),2," ")
   ;LLlat = str_get_field(header(3),2," ")
   ;cellsize = str_get_field(header(4),2," ")
   ;missing = str_get_field(header(5),2," ")
   
   
   ;create output variable
   var = new((/dimsizes(fils),nrows,ncols/),"float")

   
   ;read this first days data
   ;var(0,:,:) = (/readAsciiTable(fname,ncols,"float",(/6,9/))/)
   var(0,::-1,:) = (/readAsciiTable(fname,ncols,"float",(/6,18/))/)
   
   
   ;now for each subsequent day
   do ff = 1,dimsizes(fils)-1
     print((/ff/))
     ;get filename without the .gz
     suffix = get_file_suffix(fils(ff),0)
     fname = suffix@fBase
     
     ;open the file 
     if (suffix.eq.".gz") then
       system("gunzip "+fils(ff))
     end if
     if (suffix.eq.".Z") then
       system("uncompress "+fils(ff))
     end if

   
     
     ;var(ff,:,:) = (/readAsciiTable(fname,ncols,"float",(/6,9/))/)
     var(ff,::-1,:) = (/readAsciiTable(fname,ncols,"float",(/6,18/))/)
     
   end do
   
   
   ;create dimensions
  lat = fspan(LLlat,(LLlat + cellsize*(nrows-1)),nrows)
  lat!0 = "lat"
  lat@long_name = "Latitude"
  lat@units = "degrees_north"
  
  lon = fspan(LLlon,(LLlon + cellsize*(ncols-1)),ncols)
  lon!0 = "lon" 
  lon@long_name = "Longitude"
  lon@units = "degrees_east"
  
  if (isstring(year)) then
    iyear = stringtoint(year)
  else
    iyear = year
  end if
  time = ispan((iyear*1000)+1,(iyear*1000)+dimsizes(fils),1)
  time!0 = "time"
  time@long_name = "YYYYDDD"
  time@units = "days"
  
  
  ;create the output file
  fout = addfile(vname+"."+year+".nc","c")
  print(vname+"."+year+".nc")
  
  ;put the output file in definition mode
  setfileoption(fout,"DefineMode",True)
   
  ;create global attributes
  globatt = True
  globatt@title = "Australian Water Availability Project"
  globatt@source = "Australian Bureau of Meteorology"
  ;globatt@contact = "William Wang - X.Wang@bom.gov.au"
  globatt@creation_date = systemfunc("date")
      
  fileattdef(fout,globatt)
  
  ;define dimensionality
  dimNames = (/"time","lat","lon"/)
  dimSizes = (/-1,dimsizes(lat),dimsizes(lon)/)
  dimUnlim = (/True,False,False/)
      
  filedimdef(fout,dimNames,dimSizes,dimUnlim)
      
  ;add the variables to the file
  filevardef(fout,"time",typeof(time),getvardims(time))
  filevardef(fout,"lat",typeof(lat),getvardims(lat))
  filevardef(fout,"lon",typeof(lon),getvardims(lon))
  filevardef(fout,vname,"float",(/"time","lat","lon"/))
   
   ;add the variable attributes
  filevarattdef(fout,"time",time)
  filevarattdef(fout,"lat",lat)
  filevarattdef(fout,"lon",lon)
  
  if (vname.eq."vprp3pm") then
    var@long_name = "Daily 3pm vapour pressure"
    var@units = "hPa"
  else
  if (vname.eq."vprp9am") then
    var@long_name = "Daily 9am vapour pressure"
    var@units = "hPa"
  else
  if (vname.eq."tmax") then
    var@long_name = "Daily maximum temperature"
    var@units = "deg C"
  else
  if (vname.eq."tmin") then
    var@long_name = "Daily minimum temperature"
    var@units = "deg C"
  else
  if (vname.eq."pre") then
    var@long_name = "Daily precipitation"
    var@units = "mm"
  end if
  end if
  end if
  end if
  end if
  var@_FillValue = missing
  var@missing_value = missing
  filevarattdef(fout,vname,var)

  
  ;end the file creation
  setfileoption(fout,"DefineMode",False)
    
  ;write the dimension values
  fout->time = (/time/)
  fout->lat = (/lat/)
  fout->lon = (/lon/)
  fout->$vname$ = (/var/)
    
  print("regzipping")
  if (isvar("ydirs")) then
    system("gzip "+ydirs(dd-1)+"/*")
  else
    system("gzip "+year+"/*")
  end if
  
  delete(fout)
  delete(var)
  delete(fils)
  delete(time)
  delete(lat)
  delete(lon)
  
 end do


   
    
end    
