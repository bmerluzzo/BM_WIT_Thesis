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

static bool isInit;
void mlx90640Task(void* arg);

// Deck driver init function
static void mlx90640Init()
{

}

//Deck Driver Test Function 
static bool mlx90640Test()
{

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