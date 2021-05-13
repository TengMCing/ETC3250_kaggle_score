## WARNING: THIS IS A TERRIBLE MODEL. YOU CAN DO BETTER THAN THIS!

```r
library(tidymodels)
library(tidyverse)
```

You also need to install xgboost using install.packages('xgboost') to run this script.

For reproducibility.
```r
set.seed(32505250)
```

Load the training data
```r
mydat <- read_csv(here::here("data/release/student/student_training_release.csv"))
```

Define our model. Here we use a xgboost model. You could also choose to use other models.

We would like to choose the parameter `mtry`, `tress` and `tree_depth` using CV. Thus,
we assign them with the placeholder `tune()`. Then, we set "xgboost" as our engine.
Use `help("boost_tree")` to check the main arguments.
```r
mymodel <- boost_tree(mtry = tune(),
                      trees = tune(),
                      tree_depth = tune()) %>%
  set_engine("xgboost") %>%
  set_mode("classification")
```

Define our CV process. Here we use a 3-fold CV.
```r
mycv <- vfold_cv(mydat, v = 3, strata = "cause")
```

Define our recipe. Here we use cause as our response variable and 9 other variables
as our predictors. We first transform all the character variables to factor variables by
using `step_string2factor()`. Then, since there are some missing values in the data,
we use the knn imputation algorithm to replace NA.
However, the parameter k is unknown and we would like it to be tuned by CV.
The final step is to transform all the nominal predictors to dummy variables.
The reason to perform this step is because xgboost doesn't accept categorical
variable. You might not need to use this step for other models.
If you feel like the knn imputation takes a significant amount time to run, you could try other imputation
methods provided by recipes.
https://recipes.tidymodels.org/reference/index.html
There are also other preprocessing steps you could try.
```r
myrecipe <- recipe(mydat, formula = cause ~ ws + rf + se + maxt + mint + day + FOR_TYPE + COVER + HEIGHT) %>%
  step_string2factor(all_nominal_predictors()) %>%
  step_impute_knn(all_predictors(), neighbors = tune()) %>%
  step_dummy(all_nominal_predictors())
```

Define our workflow by adding the data preprocessing steps and model specification.
```r
myworkflow <- workflow() %>%
  add_recipe(myrecipe) %>%
  add_model(mymodel)
```

Define our tuning grid. These values are randomly chosen by me. You need to make your own
decision on this grid.
```r
mygrid <- expand.grid(mtry = c(5, 7, 9),
                      neighbors = c(3, 5),
                      trees = seq(200, 1000, 200),
                      tree_depth = c(5, 7, 9))
```

Define the tuning controller. I want some feedback during the training, so I turn on the verbose.
You could set it to FALSE.
```
mycontrol <- control_grid(verbose = TRUE)
```

Tune our parameters by using `tune_grid()`. In this function, we also need to specify the
resampling process and the tuning grid. The control is an optional argument.
Generally, parameter tuning using CV is time consuming.
```r
grid_result <- myworkflow %>%
  tune_grid(resamples = mycv, grid = mygrid, control = mycontrol)
```

plot the tuning result
```r
autoplot(grid_result)
```

From the tuning result, we need to choose the best one by providing the metric that you
are interested in. The return of `select_best()` is a tibble.
```r
mybestpara <- select_best(grid_result, metric = "accuracy")
```

Using the given tibble, we can finalize our workflow. Basically, it replaces the
placeholder `tune()` with the best values. Now, we have a complete but untrained workflow.
```r
myworkflow <- myworkflow %>%
  finalize_workflow(mybestpara)
```

The last thing we need to do is to fit our complete workflow with our data. Then, we will
have a trained workflow which can be used in prediction.
```r
myworkflow <- myworkflow %>%
  fit(data = mydat)
```

Load the prediction data.
```r
preddat <- read_csv(here::here("data/release/student/student_predict_x_release.csv"))
```

Obtaining the prediction from a workflow is easy. But you may concern about the data
transformation, the knn imputation and all other data preprocessing steps you apply on
the training set before you train the model. Will the workflow apply the same operations
on the prediction set? The answer is YES. The workflow will preprocess the prediction set
with the same recipe, and then use the trained model to predict values.
```r
mypred <- myworkflow %>%
  predict(preddat)
```

Save our prediction and ready to submit
```r
data.frame(Category = mypred$.pred_class) %>%
  mutate(Id = 1:n()) %>%
  select(Id, Category) %>%
  write_csv("__test__3.csv")
```

TAKE AWAY
1. Define your model
2. Define your CV/resampling process
3. Define your recipe/preprocessing steps
4. Add your model and recipe into the workflow
5. Define the tuning grid
6. Tuning your parameters
7. Select the best result
8. Finalize your workflow with the best set of parameters
9. Train your workflow
10. Use your workflow to make prediction

Note:
1. You could try different models provided by parsnip and some parsnip wrappers listed here
https://parsnip.tidymodels.org/reference/index.html
https://github.com/tidymodels.

2. CV is a crucial part of model selection. Simply split your data into training and test set is
acceptable but not recommended.

3. Be creative in data preprocessing, especially in feature engineering. Do some exploratory data
analysis and initial data analysis. It will help you a lot in revealing findings. Dimension
reduction such as PCA is another option you may consider.

4. If you would like to use Keras or Tensorflow model, then I will not recommend you to follow the tidymodels syntax.
Keras has its own ecosystem. Post on the forum if you need help in Keras.

5. We have shown that knn imputation can be used in handling missing values. There are many other methods.
You could also consider filter out those observations or drop those variables.
https://recipes.tidymodels.org/reference/index.html
