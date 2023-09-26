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

#define MLX90640_TASK_STACKSIZE    (2 * configMINIMAL_STACK_SIZE)
#define MLX90640_TASK_PRI 3
#define MLX90640_TASK_NAME "MLX90640"

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

}

static const DeckDriver mlx90640Driver = {
  .name = "mlx90640Deck",
  .init = mlx90640Init,
  .test = mlx90640Test,
};

DECK_DRIVER(mlx90640Driver);