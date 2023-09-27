#define DEBUG_MODULE "mlx90640Deck"

// All includes
#include "debug.h"
#include "i2cdev.h"
#include "deck.h"
#include "log.h"
#include "FreeRTOS.h"
#include "task.h"
#include "system.h"
#include "MLX90640_API.h"

#define MLX90640I2CAddr 0x33
#define MLX90640_TASK_STACKSIZE    (2 * configMINIMAL_STACK_SIZE)
#define MLX90640_TASK_PRI 3
#define MLX90640_TASK_NAME "MLX90640"
#define TA_SHIFT 8

static bool isInit;
void mlx90640Task(void* arg);

// Deck driver init function
static void mlx90640Init()
{
  if (isInit)
    return;

  DEBUG_PRINT("Initializing MLX90640...\n");
  i2cdevInit(I2C1_DEV);

  xTaskCreate(mlx90640Task, MLX90640_TASK_NAME, MLX90640_TASK_STACKSIZE, NULL, MLX90640_TASK_PRI, NULL);
  //check on stack size needed
  isInit = true;
  DEBUG_PRINT("MLX90640 initialization complete!\n");

}

//Deck Driver Test Function 
static bool mlx90640Test()
{
  DEBUG_PRINT("MLX90640Deck test\n");
  
  if (!isInit)
    return false;

  return true;
}

//Deck driver task function (collecting data and calculating temperature)
void mlx90640Task(void* arg)
{
  float emissivity = 0.95;
  float tr;
  static uint16_t eeMLX90640[832];
  static uint16_t mlx90640Frame[834];
  paramsMLX90640 mlx90640;
  static float mlx90640To[768];
  int status;
  
  systemWaitStart();
  TickType_t xLastWakeTime;

//Potentially write mode - might not because of default already set

  xLastWakeTime = xTaskGetTickCount();

  while(1) {
    vTaskDelayUntil(&xLastWakeTime, M2T()); //check on M2T function

    status = MLX90640_DumpEE(MLX90640I2CAddr, eeMLX90640);
    status = MLX90640_ExtractParameters(eeMLX90640, &mlx90640);
    status = MLX90640_GetFrameData(MLX90640I2CAddr, mlx90640Frame);

    tr = MLX90640_GetTa(mlx90640Frame, &mlx90640) - TA_SHIFT;//check TA Shift or set hardcoded value

    MLX90640_CalculateTo(mlx90640Frame, &mlx90640, emissivity, tr, mlx90640To);
  }

}

static const DeckDriver mlx90640Driver = {
  .name = "mlx90640Deck",
  .init = mlx90640Init,
  .test = mlx90640Test,
};

DECK_DRIVER(mlx90640Driver);
//add LOG functions of crazyflie