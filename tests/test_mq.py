from unittest.mock import patch, MagicMock
from services.yolo.mq import publish_yolo_output

@patch("services.yolo.mq.pika.BlockingConnection")
def test_publish_yolo_output_uses_rabbitmq(mock_connection_cls):
    mock_connection = MagicMock()
    mock_channel = MagicMock()
    mock_connection.channel.return_value = mock_channel
    mock_connection_cls.return_value = mock_connection

    payload = {"detections": [], "meta": {}}
    publish_yolo_output(payload)

    mock_connection_cls.assert_called_once()
    mock_connection.channel.assert_called_once()
    mock_channel.queue_declare.assert_called_once()
    mock_channel.basic_publish.assert_called_once()
    mock_connection.close.assert_called_once()