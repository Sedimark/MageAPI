import matplotlib.pyplot as plt
import datetime

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@custom
def analyse_predictions(data, *args, **kwargs):
    """
    Args:
        data: The output from the upstream parent block (if applicable)
        args: The output from any additional upstream blocks

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    X_test=data[0]
    ytest=data[1]
    predictions=data[2]

    print("X_test len",len(X_test))
    print("ytest len",len(ytest))
    print("predictions len",len(predictions))

    X_test_datetime = [datetime.datetime.fromtimestamp(ts[0]) for ts in X_test]

    # Extend ytest with None values for the next 3 moments
    for _ in range(3):
        ytest.append(None)

    # Plot the actual data points and predictions
    plt.figure(figsize=(12, 6))
    plt.plot(X_test_datetime, ytest, label='Actual Recorded Data')
    plt.plot(X_test_datetime, predictions, color='red', label='Predictions for test+3 future moments',marker='o')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.xticks(rotation=45)
    plt.legend()
    plt.show()
