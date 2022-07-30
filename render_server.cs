using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
 
namespace Server
{
	class Program
	{
		static void Main(string[] args)
		{
			ExecuteServer();
		}

		public static void ExecuteServer()
		{
			IPAddress ip_address = IPAddress.Parse("127.0.0.1"); //loopback ip
			IPEndPoint end_point = new IPEndPoint(ip_address, 11111); //making the endpoint
			Console.WriteLine("Server Endpoint: '{0}'\n", end_point); //FIXME diagnostic. Printing out the endpoint so we look cool lol

			//making the listener object idk
			Socket listener = new Socket(ip_address.AddressFamily, SocketType.Stream, ProtocolType.Tcp);

			try
			{
				//making sure that we only stay on our pre-approved port
				listener.Bind(end_point);
				//listening idk
				listener.Listen(10);

				//FIXME diagnostic
				Console.WriteLine("Awaiting connection ... ");

				//accepting the connection
				Socket client_socket = listener.Accept();

				byte[] bytes = new Byte[1024]; //idk
				string data = null; //initializing the data string

				while (true)
				{
					//getting the bytes
					int byte_number = client_socket.Receive(bytes);
					data = Encoding.ASCII.GetString(bytes, 0, byte_number);

					//if we are done, than we break off.
					//ecosystem.py will send "DONE" when we ^C it
					if (data == "DONE")
					{
						break;
					}

					//parsing the data, which is in format "self.__str__, self.objective, self.health, self.hunger, self.thirst, self.arousal"
					string[] stats = data.Split("; ");
					string identity = stats[0]; //this is the self.__str__() method in ecosystem.py. It contains the type, gender, position, and age
					string objective = stats[1]; //if the objective may be ""
					string target = stats[2];
					int health = Int32.Parse(stats[3]);
					double hunger = Double.Parse(stats[4]);
					double thirst = Double.Parse(stats[5]);
					double arousal = Double.Parse(stats[6]);

					Console.WriteLine("\n"+identity+" be doing action.\n  Objective: "+objective+"\n  target: "+target+"\n  Health: "+health+"\n  hunger: "+hunger+"\n  thirst: "+thirst+"\n  arousal: "+arousal);
				}
			}

			catch (Exception e)
			{
				Console.WriteLine(e.ToString());
			}
		}
	}
}
