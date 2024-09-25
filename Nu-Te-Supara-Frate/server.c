#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <pthread.h>
#include <errno.h>

#define PORT 2908
#define max_players 4

typedef struct thData{
	int idthread; //id-ul thread-ului tinut in evidenta de acest program
	int cl; //descriptorul intors de accept
	char piesa[4]; //culoarea piesei
	int pozitie; //pozitia piesei pe tabla
	char nume[20]; //numele jucatorului
	int rd; //0 daca jucatorul nu e ready, 1 altfel
	int wins; //maxim 4, de cate ori a ajuns jucatorul cu un pion in spatiul de sfarsit
	int qt; //1 daca jucatorul a dat quit
	int punct;
} thData;

struct thData jucatori[4];

//Variabile globale

int count, curent, tabla[4][46];//fiecare jucator are 45 de spatii pe care poate sa-si mute piesa
pthread_t th[100];    //Identificatorii thread-urilor care se vor crea
int puncte=4, start=0;
int qqt[4], fq=0, ps=0;
thData winner;

int check_ready();
static void *treat(void *); /*functia executata de fiecare thread, comunicarea cu clientii*/

int main()
{
  struct sockaddr_in server;	// structura folosita de server
  struct sockaddr_in from;
 
  strcpy(winner.nume,"");
  int sd;
 
  if ((sd = socket (AF_INET, SOCK_STREAM, 0)) == -1)
    {
      perror ("[server]Eroare la socket().\n");
      return errno;
    }
    
  int on=1;
  setsockopt(sd,SOL_SOCKET,SO_REUSEADDR,&on,sizeof(on));
  
  bzero (&server, sizeof (server));
  bzero (&from, sizeof (from));
  
  /* umplem structura folosita de server */
  /* stabilirea familiei de socket-uri */
    server.sin_family = AF_INET;
  /* acceptam orice adresa */
    server.sin_addr.s_addr = htonl (INADDR_ANY);
  /* utilizam un port utilizator */
    server.sin_port = htons (PORT);
  /* atasam socketul */
  
  if (bind (sd, (struct sockaddr *) &server, sizeof (struct sockaddr)) == -1)
    {
      perror ("[server]Eroare la bind().\n");
      return errno;
    }
    
  printf ("[server]Asteptam la portul %d...\n",PORT);
  
  if (listen (sd, 4) == -1)
    {
      perror ("[server]Eroare la listen().\n");
      return errno;
    }
    
  while(1)
  {
    int client;
    int length = sizeof (from);
    
    fflush (stdout);
    
    if ((client = accept (sd, (struct sockaddr *) &from, &length)) < 0)
	   {
	     perror ("[server]Eroare la accept().\n");
	     continue;
	   }
	   
    count++;
 
    if (count > 4 || start==1) 
      {
        count--;
        send(client,"Nu mai sunt locuri sau deja a inceput un joc!", 45, 0);
        close(client);
        continue;
      }
    else { 
    		jucatori[count-1].cl=client;
    		if(count==1)
    			strcpy(jucatori[count-1].piesa,"blue");
    		else if(count==2)
    			strcpy(jucatori[count-1].piesa,"pink");
    		else if(count==3)
    			strcpy(jucatori[count-1].piesa,"lime");
    		else if(count==4)
    			strcpy(jucatori[count-1].piesa,"gray");
    		jucatori[count-1].pozitie = 0;
    		jucatori[count-1].idthread = count-1;
    		tabla[count-1][0]=1; //piesele incep pe prima pozitie a tablei fiecarui jucator
    		//fiecarejucator are 4 piese dar poate sa porneasca cu o piesa noua doar dupa
    		//ce a terminat cu piesa anterioara, nu exista ciocniri sau restarturi
    		
    		pthread_create(&th[count-1], NULL, &treat, jucatori);
    	}
    
    
 }//while
 
};

int check_ready()
{
  for(int i=0;i<count;i++)
  	if(jucatori[i].rd==0)
  		{
  		  puncte=4;
  		  return 0;
  		}
  if(count>=2)
  	{
  	  start=1;
  	  return 1;
  	}
  puncte=4;
  start=0;
  return 0;
}

static void *treat(void *arg) 
{
  char comanda[100];
  int dice;
  int ccp=count-1;
  int p=count-1;
  qqt[p]=p;
  char rep[100];
  jucatori[p].qt=0;
  jucatori[p].rd=0;
  jucatori[p].wins=0;
  printf("count este: %d\n",count);
  bzero (jucatori[p].nume, 20);
  read(jucatori[p].cl, jucatori[p].nume,20);
  printf("Numele jucatorului %d este: %s\n",jucatori[p].idthread,jucatori[p].nume);
    
  write(jucatori[p].cl,"Asteapta-ti randul!",19);
      
  while(1)
    if(curent==jucatori[p].idthread)
      break;
  	
  while(1)
  {	  
  	memset(&comanda,0,100);
  	  
  	while(count<2)
  	   sleep(1);
  	  
  	if(start==0 && jucatori[curent].rd==1 && count==2)
  	  	  {
  	  	    curent=1;
  	  	    printf("am facut iful\n");
  	  	  }

  	read(jucatori[p].cl,&comanda,sizeof(comanda));
  	printf("Comanda este: %s\n",comanda);
  	
  	if(fq==0)
  		{
  		  p=qqt[p];
  		  qqt[p]=p;
  		  curent=curent%count;
  		}
  	else {
  		if(p==1)
  		  {
  		    p=0;
  		    qqt[p]=0;
  		    fq=fq-1;
  		  }
  		if(p==2)
  		  {
  		    p=1;
  		    qqt[p]=1;
  		    fq=fq-1;
  		  }
  		if(p==3)
  		  {
  		    p=2;
  		    qqt[p]=2;
  		    fq=fq-1;
  		  }
  		qqt[3]=3;
  		curent=curent%count;
  	     }
  	     
  	printf("p este: %d, iar idthread este: %d\n",p,jucatori[p].idthread);
  	printf("curent este: %d\n",curent);
  	
  	if(strcmp(comanda,"ready")!=0 && strcmp(comanda,"quit")!=0 && strcmp(comanda,"dice")!=0 && strcmp(comanda,"pause")!=0 && strcmp(comanda,"scor")!=0 && strcmp(comanda,"unpause")!=0 && strcmp("winner",comanda)!=0 && strcmp("help",comanda)!=0 && strcmp(comanda,"pozitie")!=0)
  		write(jucatori[p].cl,"Comanda invalida!",17);
  	else{
  	
       if((strcmp(comanda,"ready")==0 || strcmp(comanda,"ready\n")==0) && jucatori[curent].rd==0 && ps==0)
  	    {
  	      if(curent==jucatori[p].idthread)
  	  	    {
  	  	      write(jucatori[curent].cl,"Ai dat ready!",13);	
  	      	      jucatori[curent].rd = 1;
  	      	      curent=(curent+1)%count;
  	      	    }
  	      else write(jucatori[p].cl, "Nu este randul tau sa dai ready!",32);
  	    }
  	    
  else if((strcmp(comanda,"ready")==0 || strcmp(comanda,"ready\n")==0) && jucatori[curent].rd==0 && ps==1) 
  	 	{
  	 	  write(jucatori[p].cl,"Jocul este in pauza!",20);
  	 	}
  	 	
  	else if(strcmp(comanda,"ready")==0 && jucatori[p].rd==1 && ps==0)
  		{
  		  write(jucatori[p].cl,"Ai dat deja ready!",18);
  		}
  	else if(strcmp(comanda,"ready")==0 && jucatori[p].rd==1 && ps==1)
  		write(jucatori[p].cl,"Jocul este in pauza!",20);
  		
  	else if(check_ready()==1 && strcmp("dice",comanda)==0 && ps==0)
  	{	
  		if(curent!=jucatori[p].idthread)
  			write(jucatori[p].cl, "Nu este randul tau!",19);
  		else {
  			dice=rand()%6 + 1;
			memset(&rep,0,100);
  			if(jucatori[curent].pozitie==0)
  				{
  				  if(dice==6)
  					{
  					  tabla[curent][jucatori[curent].pozitie] = 0;
  					  jucatori[curent].pozitie += dice;
  		  			  tabla[curent][jucatori[curent].pozitie] = 1;
  		  			  sprintf(rep,"Ai dat cu zarul: %d, ai iesit din zona de start! ",dice);
  					  write(jucatori[curent].cl,rep,strlen(rep));
  		  			}
  		  		else {
  		  			sprintf(rep,"Ai dat cu zarul: %d, din pacate nu poti inainta!",dice);
  					write(jucatori[curent].cl,rep,strlen(rep));
  				     }
 				}  		  	
  		  	else {
  		  		tabla[curent][jucatori[curent].pozitie] = 0;
  		  		jucatori[curent].pozitie += dice;
  		  	 	tabla[curent][jucatori[curent].pozitie] = 1;
  		        
  		        if(jucatori[curent].pozitie<=40)
  		  	 	{ sprintf(rep,"Ai dat cu zarul: %d, foloseste pozitie pentru a afla pe ce pozitie esti!",dice);
  				  write(jucatori[curent].cl,rep,strlen(rep));
  		  	        }
  		  	       
  		  	else if(jucatori[curent].pozitie>40 && jucatori[curent].wins<3)
  		  		{
  		  		  jucatori[curent].wins++;
  		  		  jucatori[curent].punct = jucatori[curent].wins;
  		  		  tabla[curent][jucatori[curent].pozitie]=0;
  		  		  jucatori[curent].pozitie=0;
  		  		  jucatori[curent].punct+=1;
  		  		  if(jucatori[curent].wins>1)
  		  		  	sprintf(rep,"Ai dat cu zarul: %d, ai ajuns cu %d piese in spatiul de finish!",dice,jucatori[curent].wins);
  		  		  else sprintf(rep,"Ai dat cu zarul: %d, ai ajuns cu prima piesa in spatiul de finish!",dice);
  				  write(jucatori[curent].cl,rep,strlen(rep));
  		  		} 
  		  	else if(jucatori[curent].wins==3 && jucatori[curent].pozitie>40)
  		  		{
  		  		  jucatori[curent].wins++;
  		  		  jucatori[curent].punct=jucatori[curent].wins;
  		  		  write(jucatori[curent].cl,"Bravo! Ai Castigat! Jocul s-a terminat!",40);
  		  		  strcpy(winner.nume,jucatori[curent].nume);
  		  		  for(int i=0; i<count; i++)
  		  		  	{
  		  		  	  jucatori[i].wins=0;
  		  		  	  jucatori[i].rd=0;
  		  		  	  jucatori[i].punct=0;
  		  		  	  tabla[i][jucatori[i].pozitie]=0;
  		  		  	  jucatori[i].pozitie=0;
  		  		  	}
  		  		}
  		  	}
  		  		
  			curent=(curent+1)%count; 
	  	}
	}
	else if(check_ready()==1 && strcmp("dice",comanda)==0 && ps==1)
		write(jucatori[p].cl,"Jocul este in pauza!",20);
	
	else if(strcmp("dice",comanda)==0 && check_ready()==0 && ps==0) 
		{
		write(jucatori[p].cl,"Nu a dat toata lumea ready!",27);
		if(curent==jucatori[p].idthread && jucatori[p].rd==1)
			{
			  curent=(curent+1)%count;
			}
  		}
  	else if(strcmp("dice",comanda)==0 && check_ready()==0 && ps==1) 
  		write(jucatori[p].cl,"Jocul este in pauza!",20);
  		
    else if(strcmp("quit",comanda)==0)
    		{
    		  printf("1count este: %d\n",count);
    		  if(p==(count-1) && count>=2)
    		    {
    		      memset(jucatori[p].piesa,0,4);
    		      jucatori[p].pozitie=0;
    		      jucatori[p].cl=0;
    		      memset(jucatori[p].nume,0,20);
    		      jucatori[p].idthread=-1;
    		      jucatori[p].rd=0;
		      jucatori[p].wins=0;

		      count=count-1;
		      if(p==(curent-1))
		      	curent=curent%count;
		    } 	
		  else if(count>=3 && p==(count-2))
			 {		  	
		  		   strcpy(jucatori[p].piesa,jucatori[p+1].piesa);
    		      		   jucatori[p].pozitie=jucatori[p+1].pozitie;
    		      		   jucatori[p].cl=jucatori[p+1].cl;
    		      		   strcpy(jucatori[p].nume,jucatori[p+1].nume);
    		      		   jucatori[p].rd=jucatori[p+1].rd;
		      		   jucatori[p].wins=jucatori[p+1].wins;
		      		   qqt[p+1]=p;
		      		   count=count-1;
		      		   if(p < curent)
		      		   	curent=curent-1;
		         }
		  else if(count==4 && p==(count-3))
		  	{
		  	 	  strcpy(jucatori[p].piesa,jucatori[p+1].piesa);
    		      		   jucatori[p].pozitie=jucatori[p+1].pozitie;
    		      		   jucatori[p].cl=jucatori[p+1].cl;
    		      		   strcpy(jucatori[p].nume,jucatori[p+1].nume);
    		      		   jucatori[p].rd=jucatori[p+1].rd;
		      		   jucatori[p].wins=jucatori[p+1].wins;
		      		   qqt[p+1]=p;
		      		   
		      		   strcpy(jucatori[p+1].piesa,jucatori[p+2].piesa);
    		      		   jucatori[p+1].pozitie=jucatori[p+2].pozitie;
    		      		   jucatori[p+1].cl=jucatori[p+2].cl;
    		      		   strcpy(jucatori[p+1].nume,jucatori[p+2].nume);
    		      		   jucatori[p+1].rd=jucatori[p+2].rd;
		      		   jucatori[p+1].wins=jucatori[p+2].wins;
		      		   qqt[p+2]=p+1;
		      		   count=count-1;
		      		   
		      		   if(p<curent)
		      		   	curent=curent-1;
			}
		else if(count>=2 && p==0)
			{
				if(count==2)
				  {
				   strcpy(jucatori[p].piesa,jucatori[p+1].piesa);
    		      		   jucatori[p].pozitie=jucatori[p+1].pozitie;
    		      		   jucatori[p].cl=jucatori[p+1].cl;
    		      		   strcpy(jucatori[p].nume,jucatori[p+1].nume);
    		      		   jucatori[p].rd=jucatori[p+1].rd;
		      		   jucatori[p].wins=jucatori[p+1].wins;
		      		   qqt[p+1]=p;
		      		   count=count-1;
		      		   curent=curent%count;
		      		  }
		      		 else if(count==3)
		      		 	{
		      		 	  strcpy(jucatori[p].piesa,jucatori[p+1].piesa);
    		      		   	  jucatori[p].pozitie=jucatori[p+1].pozitie;
    		      		   	  jucatori[p].cl=jucatori[p+1].cl;
    		      		   	  strcpy(jucatori[p].nume,jucatori[p+1].nume);
    		      		   	  jucatori[p].rd=jucatori[p+1].rd;
		      		   	  jucatori[p].wins=jucatori[p+1].wins;
		      		   	  qqt[p+1]=p;
		      		   
		      		  	  strcpy(jucatori[p+1].piesa,jucatori[p+2].piesa);
    		      		   	  jucatori[p+1].pozitie=jucatori[p+2].pozitie;
    		      		   	  jucatori[p+1].cl=jucatori[p+2].cl;
    		      		   	  strcpy(jucatori[p+1].nume,jucatori[p+2].nume);
    		      		   	  jucatori[p+1].rd=jucatori[p+2].rd;
		      		   	  jucatori[p+1].wins=jucatori[p+2].wins;
		      		   	  qqt[p+2]=p+1;
		      		   	  
		      		   	  fq=2;
		      		   	  count=count-1;
		      		   	  if(curent!=0)
		      		   	  	curent=curent-1;
		      		 	}
		      		 else if(count==4)
		      		 	{
		      		 	  strcpy(jucatori[0].piesa,jucatori[1].piesa);
    		      		   	  jucatori[0].pozitie=jucatori[1].pozitie;
    		      		   	  jucatori[0].cl=jucatori[1].cl;
    		      		   	  strcpy(jucatori[0].nume,jucatori[1].nume);
    		      		   	  jucatori[0].rd=jucatori[1].rd;
		      		   	  jucatori[0].wins=jucatori[1].wins;
		      		   	  qqt[1]=0;
		      		   
		      		  	  strcpy(jucatori[1].piesa,jucatori[2].piesa);
    		      		   	  jucatori[1].pozitie=jucatori[2].pozitie;
    		      		   	  jucatori[1].cl=jucatori[2].cl;
    		      		   	  strcpy(jucatori[1].nume,jucatori[2].nume);
    		      		   	  jucatori[1].rd=jucatori[2].rd;
		      		   	  jucatori[1].wins=jucatori[2].wins;
		      		   	  qqt[2]=1;
		      		   	  
		      		   	  strcpy(jucatori[2].piesa,jucatori[3].piesa);
    		      		   	  jucatori[2].pozitie=jucatori[3].pozitie;
    		      		   	  jucatori[2].cl=jucatori[3].cl;
    		      		   	  strcpy(jucatori[2].nume,jucatori[3].nume);
    		      		   	  jucatori[2].rd=jucatori[3].rd;
		      		   	  jucatori[2].wins=jucatori[3].wins;
		      		   	  qqt[3]=2;
		      		   	  
		      		   	  fq=3;
		      		   	  count=count-1;
		      		   	  if(curent!=0)
		      		   	  	curent=curent-1;
		      		   	}
			}
		else if(count==1)
			{
			  for(int i=0;i<4;i++)
			    {
			  	memset(jucatori[i].piesa,0,4);
			  	tabla[i][jucatori[i].pozitie]=0;
    		      		jucatori[i].pozitie=0;
    		      		jucatori[i].cl=0;
    		      		memset(jucatori[i].nume,0,20);
    		      		jucatori[i].idthread=-1;
    		     		jucatori[i].rd=0;
		      		jucatori[i].wins=0;
		      		qqt[i]=0;
		      		jucatori[i].punct=0;
			    }
			  curent=0;
			  p=0;
			  count=0;
			  
			}
			  
		  printf("2count este: %d\n",count);
		  break;
    		}
    		
    		
    	else if(strcmp(comanda,"pause")==0)
    		{
    		if(p==curent)
    		  {
    		    if(ps==0)
    		      {
    		        ps=1;
    		    	write(jucatori[p].cl,"Ai dat pauza la joc!",20);
    		      }
    		    else write(jucatori[p].cl,"Ai dat deja pauza!",18);
    		  }
    		 else write(jucatori[p].cl,"Nu este randul tau!",19);
    		}
    	else if(strcmp(comanda,"unpause")==0)
    		{
    		  if(p==curent)
    		    {
    		      if(ps==1)
    		        {
    		          ps=0;
    		      	  write(jucatori[p].cl,"Jocul va continua!",18);
    		      	}
    		      else write(jucatori[p].cl,"Nu s-a pus nicio pauza!",23);
    		    }
    		  else write(jucatori[p].cl,"Nu este randul tau!",19);
    		}
    		
    		
    	else if(strcmp(comanda,"winner")==0)
    		{
    		  if(strcmp(winner.nume,"")==0)
    		  	write(jucatori[p].cl,"Nu a castigat nimeni inca!",26);
    		  else {
    		  	bzero(&rep,100);
    		  	sprintf(rep,"Jocul trecut a fost castigat de jucatorul %s!",winner.nume);
    		  	write(jucatori[p].cl,rep,strlen(rep));
    		  	}
    		}
    	else if(strcmp(comanda,"help")==0)
    		write(jucatori[p].cl,"Poti folosi: ready, dice, pause, unpause, help, winner, pozitie sau quit!",strlen("Poti folosi: ready, dice, pause, unpause, help, winner, pozitie sau quit!"));
        
        else if(strcmp(comanda,"pozitie")==0)
        	{
        	  bzero(&rep,100);
        	  sprintf(rep,"Esti pe pozitia %d din 40!", jucatori[p].pozitie);
        	  write(jucatori[p].cl,rep,strlen(rep));
        	}
        	
        else if(strcmp(comanda,"scor")==0)
        	{
        	  char msg[200];
        	  bzero(&msg,200);
        	  bzero(&rep,100);
        	  for(int i=0; i<count; i++)
        	  {
        	   sprintf(rep,"Jucatorul %s are scorul %d! ",jucatori[i].nume,jucatori[i].wins);
        	   strcat(msg,rep); 
        	  }
        	  write(jucatori[p].cl,msg,strlen(msg));
        	}
        
    }//else 
   check_ready();
  }//while
  
  pthread_detach(pthread_self());
  close ((intptr_t)arg);
  return(NULL);	
};	
