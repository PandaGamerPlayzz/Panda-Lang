#include <iostream>
#include <fstream>
#include <sstream>
#include <optional>
#include <vector>

#include "tokenization.hpp"
#include "parser.hpp"
#include "generation.hpp"

using namespace std;

int main(int argc, char* argv[]) {
  	if(argc != 2) {
    	cerr << "ERR: Incorrect usage. Corect Usage is:" << endl;
    	cerr << "panda <input.pnd>" << endl;

    	return EXIT_FAILURE;
  	}

	string contents;
	{	
		stringstream contents_stream;
		fstream input(argv[1], ios::in);
		contents_stream << input.rdbuf();
		contents = contents_stream.str();
	}

	Tokenizer tokenizer(std::move(contents));
	vector<Token> tokens = tokenizer.tokenize();

	Parser parser(std::move(tokens));
	std::optional<NodeExit> tree = parser.parse();

	if(!tree.has_value()) {
		std:cerr << "No exit statement found" << std::endl;
		exit(EXIT_FAILURE);
	}

	Generator generator(tree.value());
	{
		std::fstream file("./out.asm", ios::out);
		file << generator.generate();
	}

	// linux64
	system("nasm -felf64 out.asm");
	system("ld -o out out.o");

	// windows64
	// system("nasm -fwin64 out.asm");
	// system("ld -o out.exe out.obj");

  	return EXIT_SUCCESS;
}