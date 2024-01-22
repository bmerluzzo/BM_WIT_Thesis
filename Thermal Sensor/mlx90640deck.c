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
float To1[192];
float To[48];

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
        To1[((16*i)+j)/2] = (mlx90640To[(i*32)+j] + mlx90640To[(i*32)+j+1] + mlx90640To[(i*32)+j+32] + mlx90640To[(i*32)+j+33])/con;
      }
    }

    for(int i = 0;i < 12;i = i + 2){
      for(int j = 0;j < 16;j = j + 2)
        To[((i*8)+j)/2] = (To1[(i*16)+j] + To1[(i*16)+j+1] + To1[(i*16)+j+16] + To1[(i*16)+j+17])/con;
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
LOG_ADD(LOG_FLOAT, To1, &To[6])
LOG_ADD(LOG_FLOAT, To2, &To[14])
LOG_ADD(LOG_FLOAT, To3, &To[22])
LOG_ADD(LOG_FLOAT, To4, &To[30])
LOG_ADD(LOG_FLOAT, To5, &To[38])
LOG_ADD(LOG_FLOAT, To6, &To[46])
LOG_GROUP_STOP(MLX1)

LOG_GROUP_START(MLX2)
LOG_ADD(LOG_FLOAT, To1, &To[5])
LOG_ADD(LOG_FLOAT, To2, &To[13])
LOG_ADD(LOG_FLOAT, To3, &To[21])
LOG_ADD(LOG_FLOAT, To4, &To[29])
LOG_ADD(LOG_FLOAT, To5, &To[37])
LOG_ADD(LOG_FLOAT, To6, &To[45])
LOG_GROUP_STOP(MLX2)

LOG_GROUP_START(MLX3)
LOG_ADD(LOG_FLOAT, To1, &To[4])
LOG_ADD(LOG_FLOAT, To2, &To[12])
LOG_ADD(LOG_FLOAT, To3, &To[20])
LOG_ADD(LOG_FLOAT, To4, &To[28])
LOG_ADD(LOG_FLOAT, To5, &To[36])
LOG_ADD(LOG_FLOAT, To6, &To[44])
LOG_GROUP_STOP(MLX3)

LOG_GROUP_START(MLX4)
LOG_ADD(LOG_FLOAT, To1, &To[3])
LOG_ADD(LOG_FLOAT, To2, &To[11])
LOG_ADD(LOG_FLOAT, To3, &To[19])
LOG_ADD(LOG_FLOAT, To4, &To[27])
LOG_ADD(LOG_FLOAT, To5, &To[35])
LOG_ADD(LOG_FLOAT, To6, &To[43])
LOG_GROUP_STOP(MLX4)

LOG_GROUP_START(MLX5)
LOG_ADD(LOG_FLOAT, To1, &To[2])
LOG_ADD(LOG_FLOAT, To2, &To[10])
LOG_ADD(LOG_FLOAT, To3, &To[18])
LOG_ADD(LOG_FLOAT, To4, &To[26])
LOG_ADD(LOG_FLOAT, To5, &To[34])
LOG_ADD(LOG_FLOAT, To6, &To[42])
LOG_GROUP_STOP(MLX5)

LOG_GROUP_START(MLX6)
LOG_ADD(LOG_FLOAT, To1, &To[1])
LOG_ADD(LOG_FLOAT, To2, &To[9])
LOG_ADD(LOG_FLOAT, To3, &To[17])
LOG_ADD(LOG_FLOAT, To4, &To[25])
LOG_ADD(LOG_FLOAT, To5, &To[33])
LOG_ADD(LOG_FLOAT, To6, &To[41])
LOG_GROUP_STOP(MLX6)
