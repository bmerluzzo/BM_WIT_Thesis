#define DEBUG_MODULE "mlx90640Deck"

#include "debug.h"
#include "i2cdev.h"
#include "deck.h"
#include "log.h"
#include "FreeRTOS.h"
#include "task.h"
#include "system.h"
#include "MLX90640_API.h"

#define MLX90640I2CAddr 0x33
#define MLX90640_TASK_STACKSIZE    (18 * configMINIMAL_STACK_SIZE)
#define MLX90640_TASK_PRI 1
#define MLX90640_TASK_NAME "MLX90640"
#define TA_SHIFT 8
#define MLX90640_CTRL_REG 0x800D
static bool isInit;
void mlx90640Task(void* arg);
float con = 4;
float To[192];

static void mlx90640Init()
{
  if (isInit)
    return;

  DEBUG_PRINT("Initializing MLX90640...\n");
  i2cdevInit(I2C1_DEV);

  xTaskCreate(mlx90640Task, MLX90640_TASK_NAME, MLX90640_TASK_STACKSIZE, NULL, MLX90640_TASK_PRI, NULL);

  isInit = true;
  DEBUG_PRINT("MLX90640 initialization complete!\n");

}

static bool mlx90640Test()
{
  DEBUG_PRINT("MLX90640Deck test\n");

  int RR, mode;

  //MLX90640_SetRefreshRate(MLX90640I2CAddr, 4)

  RR = MLX90640_GetRefreshRate(MLX90640I2CAddr);
  DEBUG_PRINT("Current Refresh Rate:\n");
  DEBUG_PRINT("%i\n", RR);

  mode = MLX90640_GetCurMode(MLX90640I2CAddr);
  DEBUG_PRINT("Current Mode (1 if Chess Mode):\n");
  DEBUG_PRINT("%i\n", mode); 
 
  if (!isInit)
    return false;

  return true;
}

void mlx90640Task(void* arg)
{
  float emissivity = 1;
  float tr;
  static uint16_t eeMLX90640[832];
  uint16_t mlx90640Frame[834];
  paramsMLX90640 mlx90640;
  static float mlx90640To[768];
  int status;
  int count = 0;

  int test = 0;
  int test_ms;

  TickType_t start;
  TickType_t end;
  TickType_t duration;
  
  systemWaitStart();

  vTaskDelay(M2T(1080));

  status = MLX90640_DumpEE(MLX90640I2CAddr, eeMLX90640);
  status = MLX90640_ExtractParameters(eeMLX90640, &mlx90640);
  status = MLX90640_SynchFrame(MLX90640I2CAddr);

  if (status == 0){
    DEBUG_PRINT("Synch Successful");
  }

  while(1) {
    start = xTaskGetTickCount();

    if (count >= 50){
      count = 0;
      MLX90640_SynchFrame(MLX90640I2CAddr);
    }
    
    MLX90640_GetFrameData(MLX90640I2CAddr, mlx90640Frame);
    count = count + 1;
    tr = 20;
    MLX90640_CalculateTo(mlx90640Frame, &mlx90640, emissivity, tr, mlx90640To);
    MLX90640_BadPixelsCorrection((&mlx90640)->brokenPixels, mlx90640To, 1, &mlx90640)

    for(int i = 0;i < 24;i = i + 2){
      for(int j = 0;j < 32;j = j + 2){
        To[((16*i)+j)/2] = (mlx90640To[(i*32)+j] + mlx90640To[(i*32)+j+1] + mlx90640To[(i*32)+j+32] + mlx90640To[(i*32)+j+33])/con;
      }
    }

    end = xTaskGetTickCount();
    duration = end - start;

    if (test == 0){
      test_ms = T2M(duration);
      DEBUG_PRINT("%i\n", test_ms);
      test = 1;
    }

    vTaskDelay((M2T(1000) - duration));
  }

}

static const DeckDriver mlx90640Driver = {
  .name = "mlx90640Deck",
  .init = mlx90640Init,
  .test = mlx90640Test,
};

DECK_DRIVER(mlx90640Driver);

LOG_GROUP_START(MLX1)
LOG_ADD(LOG_FLOAT, To1, &To[58])
LOG_ADD(LOG_FLOAT, To2, &To[74])
LOG_ADD(LOG_FLOAT, To3, &To[90])
LOG_ADD(LOG_FLOAT, To4, &To[106])
LOG_ADD(LOG_FLOAT, To5, &To[122])
LOG_ADD(LOG_FLOAT, To6, &To[138])
LOG_GROUP_STOP(MLX1)

LOG_GROUP_START(MLX2)
LOG_ADD(LOG_FLOAT, To1, &To[57])
LOG_ADD(LOG_FLOAT, To2, &To[73])
LOG_ADD(LOG_FLOAT, To3, &To[89])
LOG_ADD(LOG_FLOAT, To4, &To[105])
LOG_ADD(LOG_FLOAT, To5, &To[121])
LOG_ADD(LOG_FLOAT, To6, &To[137])
LOG_GROUP_STOP(MLX2)

LOG_GROUP_START(MLX3)
LOG_ADD(LOG_FLOAT, To1, &To[56])
LOG_ADD(LOG_FLOAT, To2, &To[72])
LOG_ADD(LOG_FLOAT, To3, &To[88])
LOG_ADD(LOG_FLOAT, To4, &To[104])
LOG_ADD(LOG_FLOAT, To5, &To[120])
LOG_ADD(LOG_FLOAT, To6, &To[136])
LOG_GROUP_STOP(MLX3)

LOG_GROUP_START(MLX4)
LOG_ADD(LOG_FLOAT, To1, &To[55])
LOG_ADD(LOG_FLOAT, To2, &To[71])
LOG_ADD(LOG_FLOAT, To3, &To[87])
LOG_ADD(LOG_FLOAT, To4, &To[103])
LOG_ADD(LOG_FLOAT, To5, &To[119])
LOG_ADD(LOG_FLOAT, To6, &To[135])
LOG_GROUP_STOP(MLX4)

LOG_GROUP_START(MLX5)
LOG_ADD(LOG_FLOAT, To1, &To[54])
LOG_ADD(LOG_FLOAT, To2, &To[70])
LOG_ADD(LOG_FLOAT, To3, &To[86])
LOG_ADD(LOG_FLOAT, To4, &To[102])
LOG_ADD(LOG_FLOAT, To5, &To[118])
LOG_ADD(LOG_FLOAT, To6, &To[134])
LOG_GROUP_STOP(MLX5)

LOG_GROUP_START(MLX6)
LOG_ADD(LOG_FLOAT, To1, &To[53])
LOG_ADD(LOG_FLOAT, To2, &To[69])
LOG_ADD(LOG_FLOAT, To3, &To[85])
LOG_ADD(LOG_FLOAT, To4, &To[101])
LOG_ADD(LOG_FLOAT, To5, &To[117])
LOG_ADD(LOG_FLOAT, To6, &To[133])
LOG_GROUP_STOP(MLX6)