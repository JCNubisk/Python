import csv, operator
import re
import os
import sys
import time
import subprocess
import cx_Oracle
import platform
import datetime
from operator import itemgetter, attrgetter
from crontab import CronTab
from ParameterSeviciosPCM import *
from classquery import *

#Linux Mail  CAS y Windows Mail ##

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


def mail_funcion(mensaje,asunto, Usu_Mail):

    ####################################
    #Funcion para envio de mail
    ####################################
    from_address = FROM_ADDRESS
    to_address = LIST_TO_ADDRESS
    if len(Usu_Mail) > 0 :
      to_address = Usu_Mail

    ##for toaddress in to_address:
    message = mensaje
    mime_message = MIMEMultipart()
#    mime_message = MIMEText(message, "plain")
    mime_message["From"] = from_address
    mime_message["To"] = ", ".join(to_address)
    mime_message["Subject"] = asunto
    mime_message.attach(MIMEText(message, "plain"))
      
    smtp =smtplib.SMTP(SMTP_SERVER) #SMTP()

    smtp.sendmail(from_address, to_address, mime_message.as_string())
    smtp.quit()

def Usuarios_correo(UsuMail) :
    Usu_Mail=[]
    print(UsuMail)
    for Usuario in UsuMail.split(';') :
      Usu_Mail+=[Usuario.lstrip()]
    return Usu_Mail

def printf(format,*args):
  sys.stdout.write (format % args)

def printException (exception):
  MsjError=''
  error, = exception.args
  #print('Error code = %s\n'% (error.code))
  #print('Error message = %s\n'% (error.message))
  MsjError+=('Error code = %s\n'% (error.code))
  MsjError+=('Error message = %s\n'% (error.message))
  #MsjError+=("Error code = %s\n"%(error.code));
  #MsjError+=("Error message = %s\n"%(error.message));
  return MsjError

def executeConn(stringconn):
    conn=cx_Oracle.connect(stringconn)
    return conn

def executeStmt(conn, stmt,):
    if conn is not None and isinstance (conn, cx_Oracle.Connection):
        cur = conn.cursor()
        cur.execute(stmt)
    return cur


def string_crontab(HorInicio,HorFinal,MinEjecucion, IntervaloEje, DiasEjecucion):
    stringcrontab=''
    
    Vhorainicio =HorInicio
    VhoraFin =HorFinal
    Recurrencia = IntervaloEje

    ## Minutos ##
    #MinEjecucions ='0'
    #if MinEjecucion > 0:
    MinEjecucions=str(MinEjecucion)

    ## Horas ##
    Svariablehoras = ''
    if Recurrencia > 1 :
      
       while VhoraFin > Vhorainicio :
          Svariablehoras += str(Vhorainicio) + ','
          Vhorainicio += Recurrencia 
       if VhoraFin <= Vhorainicio :
          Svariablehoras += str(VhoraFin)
       else:
          Svariablehoras = Svariablehoras[:-1]
    else:
        Svariablehoras = str(Vhorainicio)+'-'+str(VhoraFin)

    DiasEje='*'
    ## Dias de la Semanan ##
    if DiasEjecucion == 'H' :
       DiasEje='1-5'
     
    
    stringcrontab=MinEjecucions+' '+Svariablehoras+' * * '+DiasEje

    return stringcrontab

 
def Row_CMONPRC_STAT(conn,tabla):
 ### PS_PUC_CMONPRC_STA -- Rows - Campos que afectan el Crontab
 #####################################################################
 ##   PUC_HORA_INI_PM       -- Hora de inicio
 ##   PUC_HORA_FIN_PM       -- Hora finalizaion 
 ##   PUC_MINUTO_INI_PM     -- Minuto en que se ejecutara el contab
 ##   REPEATRECURRENCE      -- Recurencia en hora
 ##   PUC_TIPO_DIAS_PM   DÃ­as Monitoreo
                        # H: HÃ¡biles (L a V) (default)
                        # T: Todos (L a D)
                        #
 ##   PUC_ESTADO_PM  -- AcciÃ³n Monitoreo Proceso
			#  EAC: En ActivaciÃ³n
			#  ACT: Activo
			#  EDE: En DetenciÃ³n
			#  DET: Detenido (default)

  if tabla == 'PS_PUC_MONPRC_STAT' :	
    queryvalidaregistroRP=query_variables('PS_PUC_MONPRC_STAT','Select01')
  elif tabla == 'PS_PUC_MONPRC_HIST' :
    queryvalidaregistroRP=query_variables('PS_PUC_MONPRC_HIST','Select01')
    
  curRP=executeStmt(conn, queryvalidaregistroRP)
  TablesRP = curRP.fetchall()
  OPRID=''
  PRCSNAME=''
  PUC_ESTADO_PM=''
  PUC_HORA_INI_PM=''
  PUC_HORA_FIN_PM=''
  PUC_MINUTO_INI_PM=''
  REPEATRECURRENCE=''
  PUC_TIPO_DIAS_PM=''
  for RowsRP in TablesRP:
    OPRID=RowsRP[0]
    PRCSNAME=RowsRP[1]
    PUC_ESTADO_PM=RowsRP[2]
    PUC_HORA_INI_PM=RowsRP[3]
    PUC_HORA_FIN_PM=RowsRP[4]
    PUC_MINUTO_INI_PM=RowsRP[5]
    REPEATRECURRENCE=RowsRP[6]
    PUC_TIPO_DIAS_PM=RowsRP[7]
    NOTIFY_TO=RowsRP[8]

  return OPRID,PRCSNAME,PUC_ESTADO_PM,PUC_HORA_INI_PM,PUC_HORA_FIN_PM,PUC_MINUTO_INI_PM,REPEATRECURRENCE,PUC_TIPO_DIAS_PM,NOTIFY_TO 

def Row_MONPRC_STAT(conn):
 ### PS_PUC_CMONPRC_STA -- Rows - Campos que impactan el proceso
 #####################################################################
 ##   OPRID      --  ID Usuario
 ##   PRCNAME    -- Nombre Proceso
 ##   RUNCNTLID  -- ID Control EjecuciÃ³n
 ##   RECURNAME  -- Recurrencia
 ##   PUC_MAX_MIN_ENCOL -- MÃ¡ximo de Minutos En Cola
 ##   LASTEXECDTTM -- F/H Ult. EjecuciÃ³n
 ##   FHACTUAL -- F/H Actual EjecuciÃ³n


  querydatosRP=query_variables('PS_PUC_MONPRC_STAT','Select02')
  queryvalidaregistroRP=(querydatosRP)
  curRP=executeStmt(conn, queryvalidaregistroRP)
  TablesRP = curRP.fetchall()
  OPRID=''
  PRCSNAME=''
  RUNCNTLID=''
  RECURNAME=''
  LASTEXECDTTM=''
  PFHACTUAL=''
  Ultimoprcs=''
  for RowsRP in TablesRP:
    OPRID=RowsRP[0]
    PRCSNAME=RowsRP[1]
    RUNCNTLID=RowsRP[2]
    RECURNAME=RowsRP[3]
    LASTEXECDTTM=RowsRP[4]
    FHACTUAL=RowsRP[5]
    PUC_MAX_MIN_ENCOL=RowsRP[6]
    NOTIFY_TO=RowsRP[7]
  curRP.close()
  return OPRID, PRCSNAME ,RUNCNTLID, RECURNAME, LASTEXECDTTM, FHACTUAL, PUC_MAX_MIN_ENCOL, NOTIFY_TO

def Evalura_PSPRCSRQST(conn,oprid,prcsname,runcntlid,recurname,fhultimaeje,fhactula,max_min_cola):
 ### PS_PUC_CMONPRC_STA -- Rows - Campos que impactan el proceso
 #####################################################################
 ##   OPRID      --  ID Usuario
 ##   PRCNAME    -- Nombre Proceso
 ##   RUNCNTLID  -- ID Control EjecuciÃ³n
 ##   RECURNAME  -- Recurrencia
 ##   PUC_MAX_MIN_ENCOL -- MÃ¡ximo de Minutos En Cola
 ##   LASTEXECDTTM -- F/H Ult. EjecuciÃ³n
 ##   FHACTUAL -- F/H Actual EjecuciÃ³n
 ## Variables ###

  PRCSINSTANCE =''
  RECURNAME =''
  RUNCNTLID =''
  OPRID =''
  PRCSNAME  =''
  RUNDTTM =''
  RQSTDTTM =''
  BEGINDTTM =''
  ENDDTTM =''
  STATUS ='' 
  Mensaje=''
  Mensajeerror=''
  Mensajeque=''
  SwMensajeerror=0
  SwMensajeque=0
  UltimoPRCSINSTANCE='0'
  
 ## Query  ###

  querydatosRP=query_variables('PSPRCSRQST','Select01')
  #print(querydatosRP)

  VariablesWhere={"oprid":oprid, "prcsname":prcsname,"runcntlid":runcntlid,"recurname":recurname, "fhultimaeje":fhultimaeje, "fhactula":fhactula }
  curRP = conn.cursor()
  curRP.execute(querydatosRP, VariablesWhere)
  TablesRP = curRP.fetchall()

  for RowsRP in TablesRP:
    # Asignar a cada campo el valor 
    PRCSINSTANCE = str(RowsRP[0])
    RECURNAME = str(RowsRP[1])
    RUNCNTLID = str(RowsRP[2])
    OPRID = str(RowsRP[3])
    PRCSNAME  = str(RowsRP[4])
    RUNDTTM = str(RowsRP[5])
    RQSTDTTM = str(RowsRP[6])
    BEGINDTTM = str(RowsRP[7])
    ENDDTTM = str(RowsRP[8])
    STATUS = str(RowsRP[9])

    UltimoPRCSINSTANCE=PRCSINSTANCE
    print(STATUS)
    if STATUS in ('No Success','Error'):
    #if STATUS in ('Success'):

        if SwMensajeerror == 0:
           Mensajeerror='Les informamos que se encotraron los siguiente procesos con incidencias : \n\n'
           SwMensajeerror = 1
           
        Mensajeerror+='Nombre Proceso : '+PRCSNAME+' Nro Proceso :'+PRCSINSTANCE+' Fecha de Ejecucion : '+BEGINDTTM+' Estatus :'+STATUS+'\n\n'

        print('Nombre Proceso : '+PRCSNAME+' Nro Proceso :'+PRCSINSTANCE+' Fecha de Ejecucion : '+BEGINDTTM+' Estatus :'+STATUS)
    elif STATUS in ('Queued'):
    #elif STATUS in ('Success'):
        ## Oracle DD/MM/YYYY HH24:MI:SS Python '%d/%m/%Y %H:%M:%S'
        #date_inicial_str = '2018/06/29 08:10:27'  
        date_inicial_obj = datetime.datetime.strptime(RUNDTTM, '%d/%m/%Y %H:%M:%S')
        date_final_obj = datetime.datetime.strptime(fhactula, '%d/%m/%Y %H:%M:%S')
        print(PRCSINSTANCE)
        print(PRCSNAME)
        print(RUNDTTM)
        print(fhactula)
        Horas= time.strftime("%H", time.gmtime((date_final_obj - date_inicial_obj).seconds))
        print(Horas)
        Minutos=time.strftime("%M", time.gmtime((date_final_obj - date_inicial_obj).seconds))
        print(Minutos)
        if (int(Horas) > 0 or  int(Minutos) > max_min_cola) :
           if SwMensajeque == 0:
              Mensajeque='Les informamos que se encotraron los siguiente procesos encolados : \n\n'
              SwMensajeque = 1
              
           Mensajeque+='Nombre Proceso : '+PRCSNAME+' Nro Proceso :'+PRCSINSTANCE+' Fecha de Ejecucion : '+RUNDTTM+' Estatus :'+STATUS+'\n\n'
           print('Nombre Proceso : '+PRCSNAME+' Nro Proceso :'+PRCSINSTANCE+' Fecha de Ejecucion : '+RUNDTTM+' Estatus :'+STATUS)


  curRP.close()

  if (Mensajeerror !='' or Mensajeque !='') :
      Mensaje= Mensajeerror + Mensajeque
      print(Mensaje)
      
  return UltimoPRCSINSTANCE,Mensaje


def Crear_crontab(stringcrontab,stringprograma,stringcomentario):
    cron = CronTab(user='psoft')
    job = cron.new(command=stringprograma, comment=stringcomentario)  
    job.setall(stringcrontab)
    #job.enable(False)
    cron.write()


def Modificar_crontab(stringcrontab,stringcomentario):
    cron = CronTab(user='psoft')
    exstr = stringcomentario 
    # list all cron jobs y delete el  job 
    for job in cron:
       if (re.match(r".*"+exstr+".*",job.comment )):
          job.setall(stringcrontab)
    cron.write()


def Elimiar_crontab(stringcometario):
    cron = CronTab(user='psoft')
    cron.remove_all(comment=stringcometario)
    cron.write()


def Cantidad_Rows(conn,querycount , VariablesWhere):
  ### PS_PUC_CMONPRC_STA -- Cantidad Filas
  Cantidad=0
  if conn is not None and isinstance (conn, cx_Oracle.Connection):
     if VariablesWhere != '' :
        curP = conn.cursor()
        curP.execute(querycount , VariablesWhere)
     else :
        curP = conn.cursor()
        curP.execute(querycount)
     Tables = curP.fetchall()
     Cantidad=0
     for Rows in Tables:
       Cantidad=Rows[0]
     curP.close()
  return Cantidad

def Modificar_Rows(conn, queryModificar, VariablesWhere):

  ## Delete, Update , Insert
  if conn is not None and isinstance (conn, cx_Oracle.Connection):
     if VariablesWhere != '' :
        curU = conn.cursor()
        curU.execute(queryModificar, VariablesWhere)
        conn.commit()
        curU.close()
     else :
        curI = conn.cursor()
        curI.execute(queryModificar)
        conn.commit()
        curI.close()


def Actulizar_Historico(connection,oprid, prcsname):
   #Actulizar historici borrar el registro y actulizar con el nuevo
    querydelete=query_variables('PS_PUC_MONPRC_HIST','Delete01')
    VariablesWhere={"oprid":oprid, "prcsname":prcsname}
    Modificar_Rows(connection,querydelete, VariablesWhere)
    
    queryInsert=query_variables('PS_PUC_MONPRC_HIST','Insert01')
    VariablesWhere=''
    Modificar_Rows(connection,queryInsert, VariablesWhere)




def Python_Crontab_Monitoreo():
   #########
   ########
   ## Variables
   Mensajetipo=''
   Mensajeasunto=''
   Mensaje=''
   Count_filas_CMONPRC_STAT=0
   Count_filas_MONPRC_HIST=0
   CambiarContab=0
   CambiarSoloH=0
   UsuMail=''
   UsuMailstr=''
   Usu_Mail=[]

   MsjErrorBD=''
   ErrorBD=0
   Xstringprograma = Stringprograma

   try:
     connection = executeConn(BDConnString)
   except cx_Oracle.DatabaseError as exception:
     print('Failed to connect to %s\n',BDActiva)
     MsjErrorBD=printException(exception)
     ErrorBD=1
   
   if ErrorBD !=1 :
      #querycount='select count(*) from PS_PUC_CMONPRC_STA'

      print('PS_PUC_CMONPRC_STA '+' Count01')
      querycount=query_variables('PS_PUC_CMONPRC_STA','Count01')
      VariablesWhere=''
      Count_filas_CMONPRC_STAT=Cantidad_Rows(connection, querycount, VariablesWhere)
      if Count_filas_CMONPRC_STAT != 0 :
         oprid,prcsname,Estado_pm,HorInicio,HorFinal,MinEjecucion, IntervaloEje, DiasEjecucion, UsuMail=Row_CMONPRC_STAT(connection,'PS_PUC_MONPRC_STAT')
         print(UsuMail)
         UsuMailstr=str(UsuMail)
         print(UsuMailstr)
         print('PS_PUC_MONPRC_STAT')
         Xstringcomentario = prcsname
   
         #querycount= 'select count(*) from PS_PUC_MONPRC_HIST'
         print('PS_PUC_MONPRC_HIST '+' Count01')
         querycount=query_variables('PS_PUC_MONPRC_HIST','Count01')
         VariablesWhere=''
         Count_filas_MONPRC_HIST=Cantidad_Rows(connection, querycount, VariablesWhere)
   
         if Count_filas_MONPRC_HIST != 0 :
             
            print('PS_PUC_MONPRC_HIST '+' Count02')
            querycount=query_variables('PS_PUC_MONPRC_HIST','Count02')
            VariablesWhere = ''
            Validar_Dif_Fecha = Cantidad_Rows(connection, querycount , VariablesWhere)
   
            if Validar_Dif_Fecha  != 1 :
               
               print('PS_PUC_MONPRC_HIST')
               Hoprid,Hprcsname,HEstado_pm,HHorInicio,HHorFinal,HMinEjecucion, HIntervaloEje, HDiasEjecucion, HUsuMail=Row_CMONPRC_STAT(connection,'PS_PUC_MONPRC_HIST')
               print(HUsuMail)
              
               if (HEstado_pm != Estado_pm or
                  HHorInicio != HorInicio or
                  HHorFinal != HHorFinal or
                  HMinEjecucion != MinEjecucion or 
                  HIntervaloEje  != HIntervaloEje or
                  HDiasEjecucion  !=  DiasEjecucion) :

                  CambiarContab=1
            
               else:
                
                   CambiarSoloH=1
   
         else :
               CambiarContab=1
        
   
         if CambiarContab == 1 or Estado_pm in ('EAC','EDE') :
   
              if Estado_pm in ('EAC','ACT'):
   
                 print("OPRID :"+str(oprid))
                 print("PRCSNAME :"+str(prcsname))
                 print("PUC_ESTADO_PM :"+str(Estado_pm))
                 print("PUC_HORA_INI_PM :"+str(HorInicio))
                 print("PUC_HORA_FIN_PM :"+str(HorFinal))
                 print("PUC_MINUTO_INI_PM :"+str(MinEjecucion))
                 print("REPEATRECURRENCE :"+str(IntervaloEje))
                 print("DIAS :"+str(DiasEjecucion)) 

                 ## String del Crontab ##
                 Xstringcrontab = string_crontab(HorInicio,HorFinal,MinEjecucion, IntervaloEje, DiasEjecucion)

                 print("stringcrontab :"+Xstringcrontab)

                 #Agregar una line al crontab
           
                 #Actulizar PUC_ESTADO_PM si estaba en 'EAC' a 'ACT'
                 if Estado_pm == 'EAC':
                    Crear_crontab(Xstringcrontab ,Xstringprograma ,Xstringcomentario)
                    print('PS_PUC_MONPRC_STAT '+' Update01' + 'EAC')
                    queryupdate=query_variables('PS_PUC_MONPRC_STAT','Update01')
                    VariablesWhere={"oprid":oprid, "prcsname":prcsname, "estado":'ACT' }
                    Modificar_Rows(connection,queryupdate,VariablesWhere)
                 else:
                    Modificar_crontab(Xstringcrontab,Xstringcomentario)
                 #Actulizar historici borrar el registro y actulizar con el nuevo
                 Actulizar_Historico(connection,oprid, prcsname)
    
              elif (Estado_pm in ('EDE') and Count_filas_MONPRC_HIST != 0 ):
                 #Elimina crontab
                 Elimiar_crontab(Xstringcomentario)
                 #Actulizar PUC_ESTADO_PM si estaba en 'EDE' a 'DET'
                 print('PS_PUC_MONPRC_STAT '+' Update01' + 'EDE')
                 queryupdate=query_variables('PS_PUC_MONPRC_STAT','Update01')
                 VariablesWhere={"oprid":oprid, "prcsname":prcsname, "estado":'DET' }
                 Modificar_Rows(connection,queryupdate,VariablesWhere)
                 #Actulizar historici borrar el registro y actulizar con el nuevo
                 Actulizar_Historico(connection,oprid, prcsname)

         else :
   
              if CambiarSoloH == 1 :
                 #Actulizar historici borrar el registro y actulizar con el nuevo
                  Actulizar_Historico(connection,oprid, prcsname)
  
            #####
    
      #Actulizar tabla control del monitoreo
      print('PS_PUC_CMONPRC_STA '+' Delete01')
      querydelete=query_variables('PS_PUC_CMONPRC_STA','Delete01')
      VariablesWhere={"oprid":'A', "prcsname":'B'}
      Modificar_Rows(connection,querydelete, VariablesWhere)
      print('PS_PUC_CMONPRC_STA '+' Insert01')
      queryInsert=query_variables('PS_PUC_CMONPRC_STA','Insert01')
      VariablesWhere=''
      Modificar_Rows(connection,queryInsert,VariablesWhere)

      connection.close()

   else :
  
        Mensajetipo='[ERROR-CONEXION-BD-PCM]'
        Mensajeasunto='- falla de monitoreo - problema de conexion con la BD '
        Mensaje = 'Les notificamos que hay un error en la conexion en la BD:'+BDActiva+'\n\n'
        Mensaje += 'Esto ocasiona que no se pueda agendar en el Contab el programa de monitoreo de proceso \n\n'
        Mensaje += 'El error es el siguiente: \n\n'
        Mensaje += MsjErrorBD

   Usu_Mail=Usuarios_correo(UsuMailstr)   
   print(UsuMailstr) 
   print(Usu_Mail)  
   
   return Mensajetipo,Mensajeasunto, Mensaje, Usu_Mail




def Python_Prcs_Monitoreo():

   #########
   ########
   ## Variables
   Mensajetipo=''
   Mensajeasunto=''
   Mensaje=''
   Count_filas_PSPRCSRQST=0
   ErrorBD=0
   MsjErrorBD=''
   UsuMail=''
   UsuMailstr=''
   Usu_Mail=[]

   #connection = executeConn('olmdes/olmdes@CRM92DES')

   #databaseName='CRM92DES'
   #User_pass='olmdes/olmdes1'
   try:
     print(BDConnString)
     connection = executeConn(BDConnString)
   except cx_Oracle.DatabaseError as exception:
     print('Failed to connect to %s \n'%(BDActiva))
     MsjErrorBD=printException(exception)
     ErrorBD=1

   if ErrorBD !=1 :

      oprid,prcsname,runcntlid,recurname,fhultimaeje,fhactula,max_min_cola, UsuMail =Row_MONPRC_STAT(connection) 
      UsuMailstr=str(UsuMail)
      
      querycount=query_variables('PSPRCSRQST','Count01')
      
      VariablesWhere={"oprid":oprid, "prcsname":prcsname,"runcntlid":runcntlid,"recurname":recurname, "fhultimaeje":fhultimaeje, "fhactula":fhactula }
      Count_filas_PSPRCSRQST=Cantidad_Rows(connection, querycount, VariablesWhere)
      if Count_filas_PSPRCSRQST != 0 :
          
   
          print(oprid)
          print(prcsname)
          print(runcntlid)
          print(recurname)
          print(fhultimaeje)
          print(fhactula)

 
          
          Ultimoprcs,Mensaje,=Evalura_PSPRCSRQST(connection, oprid,prcsname,runcntlid,recurname,fhultimaeje,fhactula,max_min_cola)

          if Mensaje != '' :
              
             Mensajetipo='[ADVERT-PROCESO-INCIDENCIA]'
             Mensajeasunto='- Monitoreo Procesos con incidecias   '
             #Mensajeini = 'Les informÃ³ que se encontraron los siguientes proceso con incidecias :\n'
             #Mensaje =Mensajeini+Mensaje

          #Actulizar Ultima Ejecucion y Proceso
          queryupdate=query_variables('PS_PUC_MONPRC_STAT','Update02')
          VariablesWhere={"oprid":oprid, "prcsname":prcsname,"fhactula":fhactula, "Ultimoprcs":Ultimoprcs }
          Modificar_Rows(connection,queryupdate,VariablesWhere)
          
      else :
          
          oprid,prcsname,runcntlid,recurname,fhultimaeje,fhactula,max_min_cola, UsuMail=Row_MONPRC_STAT(connection)
          Mensajetipo='[ADVERT-NO EXISTE-PROCESO]'
          Mensajeasunto='- Falla de monitoreo - No se encontro en la PSPRCSRQST registro con la combinacion  '
          Mensaje = 'Les informamos que no se encontro en la PSPRCSRQST registro con la combinacion:\n\n'
          Mensaje += 'Usuario :'+oprid+' Proceso : '+prcsname+' \n\n'
          Mensaje += 'Id de Ejecuacion :'+runcntlid+' Recurrencia: '+recurname +' \n\n'
          #Mensaje += MsjMonitor
          

          #Actulizar Ultima Ejecucion y Proceso
          queryupdate=query_variables('PS_PUC_MONPRC_STAT','Update03')
          #VariablesWhere={"oprid":'A', "prcsname":'B'}
          VariablesWhere=''
          Modificar_Rows(connection,queryupdate,VariablesWhere)

      connection.close()

   else :
        Mensajetipo='[ERROR-CONEXION-BD-PPM]'
        Mensajeasunto='- Falla de monitoreo - Problema de conexion con la BD '
        Mensaje = 'Les informamos que hay un error en la conexion en la BD:'+BDActiva+'\n\n'
        Mensaje += 'Esto ocasiona que no se pude realizar el monitoreo de los procesos \n\n'
        Mensaje += 'El error es el siguiente: \n\n'
        Mensaje += MsjErrorBD

   Usu_Mail=Usuarios_correo(UsuMailstr)
   print(UsuMailstr) 
   print(Usu_Mail)  

   return Mensajetipo,Mensajeasunto, Mensaje, Usu_Mail



