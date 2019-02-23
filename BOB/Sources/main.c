/* ###################################################################
**     Filename    : main.c
**     Project     : BOB
**     Processor   : MC9S08QE128CLK
**     Version     : Driver 01.12
**     Compiler    : CodeWarrior HCS08 C Compiler
**     Date/Time   : 2019-02-22, 17:17, # CodeGen: 0
**     Abstract    :
**         Main module.
**         This module contains user's application code.
**     Settings    :
**     Contents    :
**         No public methods
**
** ###################################################################*/
/*!
** @file main.c
** @version 01.12
** @brief
**         Main module.
**         This module contains user's application code.
*/         
/*!
**  @addtogroup main_module main module documentation
**  @{
*/         
/* MODULE main */


/* Including needed modules to compile this module/procedure */
#include "Cpu.h"
#include "Events.h"
#include "AS1.h"
#include "PTA3.h"
#include "PTD2.h"
#include "PTD3.h"
#include "PTA2.h"
/* Include shared modules, which are used for whole project */
#include "PE_Types.h"
#include "PE_Error.h"
#include "PE_Const.h"
#include "IO_Map.h"

/* User includes (#include below this line is not maintained by Processor Expert) */

void main(void)
{
  /* Write your local variable definition here */
	
	char trama[4], A[2], B[2];
	//bool D0 = 0,D1 = 1,D2 = 0,D3 = 1;
	word ptr;

  /*** Processor Expert internal initialization. DON'T REMOVE THIS CODE!!! ***/
  PE_low_level_init();
  /*** End of Processor Expert internal initialization.                    ***/

  /* Write your code here */
  /* For example: for(;;) { } */
  
  for(;;){
	  
	  /*//Adquisici�n de se�ales anal�gicas
	      //Recordar activar el ADC antes de descomentar
	  	  AD1_Measure(TRUE);
	  	  AD1_GetChanValue16(0,A); //Canal 0 
	  	  AD1_GetChanValue16(1,B); //Canal 1
	  	  
	  	  //Preajuste para el entramado
	  	  A[1] = A[1]>>4 | A[0]<<4;
	  	  A[0] = A[0]>>4;
	  	  B[1] = B[1]>>4 | B[0]<<4;
	  	  B[0] = B[0]>>4;	  	 
	  */	  
	  	  
	  	  //Valores fijos para hacer pruebas
	      A[0] = (char )10; 
	      A[1] = (char )120;
	      B[0] = (char )3;
	      B[1] = (char )94;
	  	  
	  	  //Entramado
	  	  trama[0] = (A[0] << 2 | A[1] >> 6) & 0b00111111;
	  	  trama[1] = (A[1] & 0b00111111) | 0b10000000;
	  	  trama[2] = (B[0] << 2 | B[1] >> 6) | 0b10000000;
	  	  trama[3] = (B[1] & 0b00111111) | 0b10000000;
	  	  
	  	  
	  	  //Adquisici�n de se�ales digitales y su inclusi�n en la trama
	  	  //Canal D0
	  	  if(PTA2_GetVal() == 0){
	  		  trama[0] = trama[0] & 0b10111111;
	  	  }else{
	  		  trama[0] = trama[0] | 0b01000000;
	  	  }
	  	  //Canal D1
	  	  if(PTA3_GetVal() == 0){
	  		  trama[1] = trama[1] & 0b10111111;
	  	  }else{
	  		  trama[1] = trama[1] | 0b01000000;
	  	  }
	  	  //Canal D2
	  	  if(PTD2_GetVal() == 0){
	  		  trama[2] = trama[2] & 0b10111111;
	  	  }else{
	  		  trama[2] = trama[2] | 0b01000000;
	  	  }
	  	  //Canal D3
	  	  if(PTD3_GetVal() == 0){
	  		  trama[3] = trama[3] & 0b10111111;
	  	  }else{
	  		  trama[3] = trama[3] | 0b01000000;
	  	}
	  
	      AS1_SendBlock(trama,sizeof(trama),&ptr);
	  	  Cpu_Delay100US(10000);
	  	  
	  
	  
	  
  }
  
  
  

  /*** Don't write any code pass this line, or it will be deleted during code generation. ***/
  /*** RTOS startup code. Macro PEX_RTOS_START is defined by the RTOS component. DON'T MODIFY THIS CODE!!! ***/
  #ifdef PEX_RTOS_START
    PEX_RTOS_START();                  /* Startup of the selected RTOS. Macro is defined by the RTOS component. */
  #endif
  /*** End of RTOS startup code.  ***/
  /*** Processor Expert end of main routine. DON'T MODIFY THIS CODE!!! ***/
  for(;;){}
  /*** Processor Expert end of main routine. DON'T WRITE CODE BELOW!!! ***/
} /*** End of main routine. DO NOT MODIFY THIS TEXT!!! ***/

/* END main */
/*!
** @}
*/
/*
** ###################################################################
**
**     This file was created by Processor Expert 10.3 [05.09]
**     for the Freescale HCS08 series of microcontrollers.
**
** ###################################################################
*/