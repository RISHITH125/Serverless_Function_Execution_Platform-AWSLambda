from abc import ABC, abstractmethod

class ContainerRuntime(ABC):

    @abstractmethod
    def build_image(self, language):
        pass

    @abstractmethod
    def start_container(self, language):
        pass

    @abstractmethod
    def stop_container(self, container):
        pass

    @abstractmethod
    def exec_function(self, container, code, args, language):
        pass

    @abstractmethod
    def is_container_alive(self, container):
        pass

